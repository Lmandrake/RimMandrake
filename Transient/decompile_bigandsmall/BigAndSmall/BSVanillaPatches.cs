using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class BSVanillaPatches
{
	[HarmonyPatch(typeof(LifeStageWorker), "Notify_LifeStageStarted")]
	[HarmonyPostfix]
	public static void Post_Notify_LifeStageStarted(Pawn pawn)
	{
		HumanoidPawnScaler.ShedueleForceRegenerateSafe(pawn, 100);
	}
}
