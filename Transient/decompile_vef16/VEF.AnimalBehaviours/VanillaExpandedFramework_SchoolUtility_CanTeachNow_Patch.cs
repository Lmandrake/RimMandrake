using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(SchoolUtility))]
[HarmonyPatch("CanTeachNow")]
public static class VanillaExpandedFramework_SchoolUtility_CanTeachNow_Patch
{
	[HarmonyPrefix]
	public static bool RemoveTeaching(Pawn teacher)
	{
		if (StaticCollectionsClass.draftable_animals.Contains((Thing)(object)teacher))
		{
			return false;
		}
		return true;
	}
}
