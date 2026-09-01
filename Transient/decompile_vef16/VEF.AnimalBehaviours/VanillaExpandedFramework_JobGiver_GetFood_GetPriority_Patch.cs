using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(JobGiver_GetFood))]
[HarmonyPatch("TryGiveJob")]
public static class VanillaExpandedFramework_JobGiver_GetFood_GetPriority_Patch
{
	[HarmonyPrefix]
	public static bool StopEatingThings(Pawn pawn)
	{
		if (StaticCollectionsClass.weirdEaters_animals.Contains((Thing)(object)pawn))
		{
			return false;
		}
		return true;
	}
}
