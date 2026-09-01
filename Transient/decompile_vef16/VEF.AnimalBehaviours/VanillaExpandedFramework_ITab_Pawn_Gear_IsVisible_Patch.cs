using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(ITab_Pawn_Gear))]
[HarmonyPatch("ShouldShowEquipment")]
public static class VanillaExpandedFramework_ITab_Pawn_Gear_IsVisible_Patch
{
	[HarmonyPostfix]
	private static void RemoveTab(Pawn p, ref bool __result)
	{
		if (StaticCollectionsClass.draftable_animals.Contains((Thing)(object)p))
		{
			__result = false;
		}
	}
}
