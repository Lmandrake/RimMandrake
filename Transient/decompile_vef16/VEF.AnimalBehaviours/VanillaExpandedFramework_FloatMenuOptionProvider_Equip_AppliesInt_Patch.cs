using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(FloatMenuOptionProvider_Equip))]
[HarmonyPatch("AppliesInt")]
public static class VanillaExpandedFramework_FloatMenuOptionProvider_Equip_AppliesInt_Patch
{
	[HarmonyPostfix]
	private static void NoWeaponEquipping(FloatMenuContext context, ref bool __result)
	{
		if (StaticCollectionsClass.draftable_animals.Contains((Thing)(object)context.FirstSelectedPawn) && !StaticCollectionsClass.canEquipWeapon_animals.Contains((Thing)(object)context.FirstSelectedPawn))
		{
			__result = false;
		}
	}
}
