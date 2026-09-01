using HarmonyLib;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Pawn_EquipmentTracker), "AddEquipment")]
public static class VanillaExpandedFramework_Pawn_EquipmentTracker_AddEquipment_Patch
{
	public static void Postfix(Pawn_EquipmentTracker __instance, ref ThingWithComps newEq)
	{
		ThingCompUtility.TryGetComp<CompWeaponHediffs>((Thing)(object)newEq)?.AssignHediffs();
	}
}
