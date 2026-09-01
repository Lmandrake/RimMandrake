using HarmonyLib;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(Hediff_Pregnant), "PostAdd")]
public static class VanillaExpandedFramework_Hediff_Pregnant_PostAdd_Patch
{
	[HarmonyPostfix]
	public static void CauseEggFertilization(Hediff_Pregnant __instance, Pawn ___father)
	{
		foreach (Hediff item in ((Hediff)__instance).pawn?.health?.hediffSet?.hediffs)
		{
			if (HediffUtility.TryGetComp<HediffComp_HumanEggLayer>(item) == null)
			{
				continue;
			}
			HediffComp_HumanEggLayer hediffComp_HumanEggLayer = ((item != null) ? HediffUtility.TryGetComp<HediffComp_HumanEggLayer>(item) : null);
			hediffComp_HumanEggLayer.DisableNormalPregnancy();
			if (hediffComp_HumanEggLayer.FullyFertilized)
			{
				continue;
			}
			hediffComp_HumanEggLayer.Fertilize(___father);
			if (___father?.genes != null)
			{
				foreach (Gene endogene in ___father.genes.Endogenes)
				{
					hediffComp_HumanEggLayer.fatherGenes.Add(endogene.def);
				}
			}
			if (((Hediff)__instance).pawn.genes == null)
			{
				continue;
			}
			foreach (Gene endogene2 in ((Hediff)__instance).pawn.genes.Endogenes)
			{
				hediffComp_HumanEggLayer.motherGenes.Add(endogene2.def);
			}
		}
	}
}
