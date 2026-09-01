using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class EquipNotifyPatches
{
	[HarmonyPatch(typeof(Thing), "Notify_Equipped")]
	[HarmonyPostfix]
	public static void Notify_Notify_Equipped(Thing __instance, Pawn pawn)
	{
		HumanoidPawnScaler.GetInvalidateLater(pawn, 1);
	}

	[HarmonyPostfix]
	[HarmonyPatch(typeof(Thing), "Notify_Unequipped")]
	public static void Notify_Notify_Unequipped(Thing __instance, Pawn pawn)
	{
		HumanoidPawnScaler.GetInvalidateLater(pawn, 1);
	}

	[HarmonyPatch(typeof(Pawn_EquipmentTracker), "Notify_EquipmentAdded")]
	[HarmonyPostfix]
	public static void Notify_EquipmentAdded(Pawn_EquipmentTracker __instance, ThingWithComps eq)
	{
		Pawn pawn = __instance.pawn;
		if (pawn != null)
		{
			HumanoidPawnScaler.GetInvalidateLater(pawn, 1);
		}
	}

	[HarmonyPostfix]
	[HarmonyPatch(typeof(Pawn_EquipmentTracker), "Notify_EquipmentRemoved")]
	public static void Notify_Notify_EquipmentRemoved(Pawn_EquipmentTracker __instance, ThingWithComps eq)
	{
		Pawn pawn = __instance.pawn;
		if (pawn != null)
		{
			HumanoidPawnScaler.GetInvalidateLater(pawn, 1);
		}
	}
}
