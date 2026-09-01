using HarmonyLib;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Pawn_EquipmentTracker), "Notify_EquipmentRemoved")]
public static class VanillaExpandedFramework_Pawn_EquipmentTracker_Notify_EquipmentRemoved_Patch
{
	public static void Postfix(Pawn_EquipmentTracker __instance, ThingWithComps eq)
	{
		ApparelExtensionUtilities.UnequipGear(__instance.pawn, (Thing)(object)eq);
	}
}
