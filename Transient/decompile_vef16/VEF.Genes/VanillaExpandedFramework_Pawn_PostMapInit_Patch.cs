using HarmonyLib;
using VEF.AestheticScaling;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(Pawn), "PostMapInit")]
public static class VanillaExpandedFramework_Pawn_PostMapInit_Patch
{
	public static void Postfix(Pawn __instance)
	{
		if (__instance != null)
		{
			PawnDataCache.GetPawnDataCache(__instance, forceRefresh: true);
		}
	}
}
