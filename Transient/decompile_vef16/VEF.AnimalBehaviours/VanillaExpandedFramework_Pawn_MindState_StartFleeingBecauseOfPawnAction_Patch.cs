using HarmonyLib;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(Pawn_MindState))]
[HarmonyPatch("StartFleeingBecauseOfPawnAction")]
public static class VanillaExpandedFramework_Pawn_MindState_StartFleeingBecauseOfPawnAction_Patch
{
	[HarmonyPrefix]
	public static bool DontFlee(Pawn_MindState __instance)
	{
		if (StaticCollectionsClass.nofleeing_animals.Contains((Thing)(object)__instance.pawn))
		{
			return false;
		}
		return true;
	}
}
