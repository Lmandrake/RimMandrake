using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_Verb_MeleeAttack_SoundHitPawn_Patch
{
	public static void ChangeMeleeSound(ref SoundDef __result, Verb_MeleeAttack __instance)
	{
		if (((Verb)__instance).EquipmentSource == null || !StaticCollectionsClass.uniqueWeaponsInGame.Contains(((Thing)((Verb)__instance).EquipmentSource).def))
		{
			return;
		}
		ThingWithComps equipmentSource = ((Verb)__instance).EquipmentSource;
		CompUniqueWeapon val = ((equipmentSource != null) ? equipmentSource.GetComp<CompUniqueWeapon>() : null);
		if (val == null)
		{
			return;
		}
		foreach (WeaponTraitDef item in val.TraitsListForReading)
		{
			WeaponTraitDefExtension modExtension = ((Def)item).GetModExtension<WeaponTraitDefExtension>();
			if (modExtension?.meleeSoundOverride != null)
			{
				__result = modExtension.meleeSoundOverride;
			}
		}
	}
}
