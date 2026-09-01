using System.Collections.Generic;
using System.Linq;
using VEF.Things;
using Verse;

namespace VEF.Apparels;

[StaticConstructorOnStartup]
public static class VanillaShieldsExpandedStartup
{
	public static bool anyShieldItemPresent;

	public static bool isSettingValues;

	static VanillaShieldsExpandedStartup()
	{
		anyShieldItemPresent = DefDatabase<ThingDef>.AllDefs.Any((ThingDef x) => x.GetCompProperties<CompProperties_Shield>() != null);
		if (VanillaShieldsExpandedSettings.usableWithShieldsWeapons == null)
		{
			VanillaShieldsExpandedSettings.usableWithShieldsWeapons = new Dictionary<string, bool>();
		}
		VanillaShieldsExpandedSettings.allWeapons = DefDatabase<ThingDef>.AllDefs.Where((ThingDef x) => x.IsWeapon && !x.destroyOnDrop).ToList();
	}

	public static void SetValues()
	{
		if (isSettingValues)
		{
			return;
		}
		isSettingValues = true;
		foreach (ThingDef allWeapon in VanillaShieldsExpandedSettings.allWeapons)
		{
			if (!VanillaShieldsExpandedSettings.usableWithShieldsWeapons.TryGetValue(((Def)allWeapon).defName, out var _))
			{
				VanillaShieldsExpandedSettings.usableWithShieldsWeapons[((Def)allWeapon).defName] = allWeapon.UsableWithShields();
			}
			if (!VanillaShieldsExpandedSettings.usableWithShieldsWeapons.TryGetValue(((Def)allWeapon).defName, out var value2))
			{
				continue;
			}
			ThingDefExtension thingDefExtension = ((Def)allWeapon).GetModExtension<ThingDefExtension>();
			if (value2 && thingDefExtension == null)
			{
				ThingDef val = allWeapon;
				if (((Def)val).modExtensions == null)
				{
					((Def)val).modExtensions = new List<DefModExtension>();
				}
				thingDefExtension = new ThingDefExtension();
				((Def)allWeapon).modExtensions.Add((DefModExtension)(object)thingDefExtension);
			}
			if (thingDefExtension != null)
			{
				thingDefExtension.usableWithShields = value2;
			}
		}
		isSettingValues = true;
	}
}
