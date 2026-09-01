using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_CompUniqueWeapon_AddTrait_Patch
{
	public static void HandleExtendedWorker(WeaponTraitDef traitDef, CompUniqueWeapon __instance)
	{
		if (traitDef.Worker is WeaponTraitWorker_Extended weaponTraitWorker_Extended)
		{
			weaponTraitWorker_Extended.Notify_Added((Thing)(object)((ThingComp)__instance).parent);
		}
		ThingWithComps parent = ((ThingComp)__instance).parent;
		if (parent != null)
		{
			parent.GetComp<CompApplyWeaponTraits>()?.DeleteCaches();
		}
	}
}
