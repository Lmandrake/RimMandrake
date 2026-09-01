using HarmonyLib;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Pawn_EquipmentTracker), "ExposeData")]
public static class VanillaExpandedFramework_Pawn_EquipmentTracker_ExposeData_Patch
{
	private static void Postfix(Pawn_EquipmentTracker __instance)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Invalid comparison between Unknown and I4
		if ((int)Scribe.mode != 4 || __instance.AllEquipmentListForReading == null)
		{
			return;
		}
		foreach (ThingWithComps item in __instance.AllEquipmentListForReading)
		{
			ApparelExtensionUtilities.EquipGear(__instance.pawn, (Thing)(object)item);
		}
	}
}
