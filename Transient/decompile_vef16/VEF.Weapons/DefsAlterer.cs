using System.Collections.Generic;
using Verse;

namespace VEF.Weapons;

[StaticConstructorOnStartup]
public static class DefsAlterer
{
	static DefsAlterer()
	{
		Setup();
		DoDefsAlter();
	}

	public static void Setup()
	{
		foreach (ThingDef item in DefDatabase<ThingDef>.AllDefsListForReading)
		{
			if (((Def)item).HasModExtension<HeavyWeapon>())
			{
				HeavyWeaponsMod.heavyWeaponsExist = true;
				if (HeavyWeaponsMod.settings.weaponStates == null)
				{
					HeavyWeaponsMod.settings.weaponStates = new Dictionary<string, bool>();
				}
				if (HeavyWeaponsMod.settings.weaponHPStates == null)
				{
					HeavyWeaponsMod.settings.weaponHPStates = new Dictionary<string, int>();
				}
				if (!HeavyWeaponsMod.settings.weaponStates.ContainsKey(((Def)item).defName))
				{
					HeavyWeaponsMod.settings.weaponStates[((Def)item).defName] = true;
				}
				if (!HeavyWeaponsMod.settings.weaponHPStates.ContainsKey(((Def)item).defName))
				{
					HeavyWeapon modExtension = ((Def)item).GetModExtension<HeavyWeapon>();
					HeavyWeaponsMod.settings.weaponHPStates[((Def)item).defName] = modExtension.weaponHitPointsDeductionOnShot;
				}
			}
		}
	}

	public static void DoDefsAlter()
	{
		foreach (KeyValuePair<string, bool> weaponState in HeavyWeaponsMod.settings.weaponStates)
		{
			if (!weaponState.Value)
			{
				ThingDef namedSilentFail = DefDatabase<ThingDef>.GetNamedSilentFail(weaponState.Key);
				if (namedSilentFail != null)
				{
					((Def)namedSilentFail).GetModExtension<HeavyWeapon>().weaponHitPointsDeductionOnShot = 0;
				}
			}
		}
		foreach (KeyValuePair<string, int> weaponHPState in HeavyWeaponsMod.settings.weaponHPStates)
		{
			ThingDef namedSilentFail2 = DefDatabase<ThingDef>.GetNamedSilentFail(weaponHPState.Key);
			if (namedSilentFail2 != null)
			{
				HeavyWeapon modExtension = ((Def)namedSilentFail2).GetModExtension<HeavyWeapon>();
				if (modExtension.weaponHitPointsDeductionOnShot != weaponHPState.Value)
				{
					modExtension.weaponHitPointsDeductionOnShot = weaponHPState.Value;
				}
			}
		}
	}
}
