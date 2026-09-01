using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Genes;

[HarmonyPatch(typeof(JobDriver_Vomit))]
[HarmonyPatch("MakeNewToils")]
public static class VanillaExpandedFramework_JobDriver_Vomit_MakeNewToils_Patch
{
	public static Pawn curPawn;

	[HarmonyPrefix]
	public static void StorePawn(JobDriver_Vomit __instance)
	{
		curPawn = ((JobDriver)__instance).pawn;
	}
}
