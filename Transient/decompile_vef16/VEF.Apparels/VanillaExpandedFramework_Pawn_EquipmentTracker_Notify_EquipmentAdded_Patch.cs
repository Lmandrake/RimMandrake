using HarmonyLib;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Pawn_EquipmentTracker), "Notify_EquipmentAdded")]
public static class VanillaExpandedFramework_Pawn_EquipmentTracker_Notify_EquipmentAdded_Patch
{
	public static void Postfix(Pawn_EquipmentTracker __instance, ThingWithComps eq)
	{
		ApparelExtensionUtilities.EquipGear(__instance.pawn, (Thing)(object)eq);
	}
}
