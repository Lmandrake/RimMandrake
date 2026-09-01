using HarmonyLib;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(Gene), "PostAdd")]
public static class VanillaExpandedFramework_Gene_PostAdd_Patch
{
	public static void Postfix(Gene __instance)
	{
		if (!PawnGenerator.IsBeingGenerated(__instance.pawn) && __instance.Active)
		{
			GeneUtils.ApplyGeneEffects(__instance);
		}
	}
}
