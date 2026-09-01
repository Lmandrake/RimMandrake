using HarmonyLib;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Pawn_EquipmentTracker), "TryDropEquipment")]
public static class VanillaExpandedFramework_Pawn_EquipmentTracker_TryDropEquipment_Patch
{
	public static void Postfix(Pawn_EquipmentTracker __instance, ThingWithComps eq, ThingWithComps resultingEq, IntVec3 pos, bool forbid = true)
	{
		ThingCompUtility.TryGetComp<CompWeaponHediffs>((Thing)(object)resultingEq)?.AssignHediffs();
	}
}
