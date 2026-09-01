using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_Verb_LaunchProjectile_Projectile_Patch
{
	public static void ChangeProjectile(ref ThingDef __result, Verb_LaunchProjectile __instance)
	{
		if (__result != ((Verb)__instance).verbProps.defaultProjectile || ((Verb)__instance).EquipmentSource == null || !StaticCollectionsClass.uniqueWeaponsInGame.Contains(((Thing)((Verb)__instance).EquipmentSource).def))
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
			if (modExtension == null)
			{
				continue;
			}
			if (modExtension.randomprojectiles)
			{
				__result = GenCollection.RandomElement<ThingDef>((IEnumerable<ThingDef>)StaticCollectionsClass.projectilesInGame);
				if (!modExtension.lowPreferenceProjectileOverride)
				{
					break;
				}
			}
			else if (!GenDictionary.NullOrEmpty<ThingDef, ThingDef>(modExtension.projectileOverrides) && modExtension.projectileOverrides.ContainsKey(((Thing)((Verb)__instance).EquipmentSource).def))
			{
				__result = modExtension.projectileOverrides[((Thing)((Verb)__instance).EquipmentSource).def];
				if (!modExtension.lowPreferenceProjectileOverride)
				{
					break;
				}
			}
			else if (modExtension.projectileOverride != null)
			{
				__result = modExtension.projectileOverride;
				if (!modExtension.lowPreferenceProjectileOverride)
				{
					break;
				}
			}
		}
	}
}
