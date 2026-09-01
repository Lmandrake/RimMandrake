using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(Building_OutfitStand))]
[HarmonyPatch("GetFloatMenuOptionToEquipWeapon")]
public static class VanillaExpandedFramework_Building_OutfitStand_GetFloatMenuOptionToEquipWeapon_Patch
{
	[HarmonyPostfix]
	private static void NoWeaponEquipping(Pawn selPawn, ref FloatMenuOption __result)
	{
		if (StaticCollectionsClass.draftable_animals.Contains((Thing)(object)selPawn) && !StaticCollectionsClass.canEquipWeapon_animals.Contains((Thing)(object)selPawn))
		{
			__result = null;
		}
	}
}
