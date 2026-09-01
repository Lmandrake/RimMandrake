using HarmonyLib;
using RimWorld;
using VEF.AestheticScaling;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(Pawn_GeneTracker), "Notify_GenesChanged")]
public static class VanillaExpandedFramework_Notify_GenesChanged_Patch
{
	[HarmonyPostfix]
	public static void Postfix(GeneDef addedOrRemovedGene, Pawn_GeneTracker __instance)
	{
		if (__instance?.pawn != null)
		{
			PawnDataCache.GetPawnDataCache(__instance.pawn, forceRefresh: true);
		}
	}
}
