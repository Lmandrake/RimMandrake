using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[StaticConstructorOnStartup]
public static class StaticCollectionsClass
{
	public static List<ThingDef> projectilesInGame;

	public static List<ThingDef> uniqueWeaponsInGame;

	static StaticCollectionsClass()
	{
		projectilesInGame = new List<ThingDef>();
		uniqueWeaponsInGame = new List<ThingDef>();
		if (!ModsConfig.OdysseyActive)
		{
			return;
		}
		List<ThingDef> list = (uniqueWeaponsInGame = DefDatabase<ThingDef>.AllDefsListForReading.Where((ThingDef x) => x.GetCompProperties<CompProperties_UniqueWeapon>() != null).ToList());
		if (list.Count > 0)
		{
			foreach (ThingDef item in list)
			{
				item.comps.Add((CompProperties)(object)new CompProperties_ApplyWeaponTraits());
			}
		}
		projectilesInGame = DefDatabase<ThingDef>.AllDefsListForReading.Where(delegate(ThingDef x)
		{
			if (x.projectile != null)
			{
				ProjectileExtension modExtension = ((Def)x).GetModExtension<ProjectileExtension>();
				if (modExtension == null)
				{
					return true;
				}
				return !modExtension.excludeFromStaticCollection;
			}
			return false;
		}).ToList();
	}
}
