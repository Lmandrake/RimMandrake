using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(Pawn_FilthTracker))]
[HarmonyPatch("Notify_EnteredNewCell")]
public static class VanillaExpandedFramework_Pawn_FilthTracker_Notify_EnteredNewCell_Patch
{
	[HarmonyPrefix]
	public static bool DontDealWithFilth(Pawn ___pawn)
	{
		if (StaticCollectionsClass.nofilth_animals.Contains((Thing)(object)___pawn))
		{
			return false;
		}
		return true;
	}
}
