using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_Pawn_EquipmentTracker_Notify_AbilityUsed_Patch
{
	public static void NotifyAbilityUses(Ability ability, Pawn_EquipmentTracker __instance)
	{
		ThingWithComps primary = __instance.Primary;
		CompApplyWeaponTraits compApplyWeaponTraits = ((primary != null) ? primary.GetComp<CompApplyWeaponTraits>() : null);
		if (compApplyWeaponTraits != null && ability.def == compApplyWeaponTraits.abilityWithCharges)
		{
			compApplyWeaponTraits.Notify_UsedAbility();
		}
	}
}
