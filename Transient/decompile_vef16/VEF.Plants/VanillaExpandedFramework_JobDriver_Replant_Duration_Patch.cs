using HarmonyLib;
using RimWorld;
using Verse.AI;

namespace VEF.Plants;

[HarmonyPatch(typeof(JobDriver_Replant))]
[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_JobDriver_Replant_Duration_Patch
{
	[HarmonyPrefix]
	public static bool AvoidError(JobDriver_Replant __instance, ref int __result)
	{
		if (((JobDriver_HaulToContainer)__instance).ThingToCarry is MinifiedFlower)
		{
			__result = 200;
			return false;
		}
		return true;
	}
}
