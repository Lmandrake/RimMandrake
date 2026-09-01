using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(PawnRenderNode), "ColorFor")]
public static class VanillaExpandedFramework_PawnRenderNode_ColorFor_Patch
{
	public static void Postfix(PawnRenderNode __instance, Pawn pawn, ref Color __result)
	{
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		if (__instance.gene == null)
		{
			return;
		}
		GeneExtension modExtension = ((Def)__instance.gene.def).GetModExtension<GeneExtension>();
		if (modExtension?.applySkinColorWithGenes == null)
		{
			return;
		}
		foreach (GeneDef applySkinColorWithGene in modExtension.applySkinColorWithGenes)
		{
			Gene gene = pawn.genes.GetGene(applySkinColorWithGene);
			if (gene != null && gene.Active)
			{
				__result = pawn.story.SkinColor;
				break;
			}
		}
	}
}
