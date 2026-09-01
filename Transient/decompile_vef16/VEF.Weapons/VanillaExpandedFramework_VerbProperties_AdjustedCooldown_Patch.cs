using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_VerbProperties_AdjustedCooldown_Patch
{
	public static void RandomizeCooldown(ref float __result, Thing equipment)
	{
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		if (equipment == null || !StaticCollectionsClass.uniqueWeaponsInGame.Contains(equipment.def))
		{
			return;
		}
		CompUniqueWeapon val = ThingCompUtility.TryGetComp<CompUniqueWeapon>(equipment);
		if (val == null)
		{
			return;
		}
		foreach (WeaponTraitDef item in val.TraitsListForReading)
		{
			WeaponTraitDefExtension modExtension = ((Def)item).GetModExtension<WeaponTraitDefExtension>();
			if (modExtension != null && modExtension.coolDownRange != FloatRange.Zero)
			{
				__result *= ((FloatRange)(ref modExtension.coolDownRange)).RandomInRange;
			}
		}
	}
}
