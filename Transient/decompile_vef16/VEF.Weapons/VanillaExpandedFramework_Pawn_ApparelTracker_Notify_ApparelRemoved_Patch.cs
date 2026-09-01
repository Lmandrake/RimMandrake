using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Pawn_ApparelTracker), "Notify_ApparelRemoved")]
public static class VanillaExpandedFramework_Pawn_ApparelTracker_Notify_ApparelRemoved_Patch
{
	public static void Postfix(Pawn_ApparelTracker __instance)
	{
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		Pawn_EquipmentTracker equipment = __instance.pawn.equipment;
		ThingWithComps val = ((equipment != null) ? equipment.Primary : null);
		if (val != null)
		{
			HeavyWeapon modExtension = ((Def)((Thing)val).def).GetModExtension<HeavyWeapon>();
			if (modExtension != null && modExtension.isHeavy && !VanillaExpandedFramework_EquipmentUtility_CanEquip_Patch.CanEquip((Thing)(object)val, __instance.pawn, modExtension))
			{
				ThingWithComps val2 = default(ThingWithComps);
				__instance.pawn.equipment.TryDropEquipment(val, ref val2, ((Thing)__instance.pawn).Position, true);
			}
		}
	}
}
