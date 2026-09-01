using UnityEngine;
using Verse;

namespace VEF.Weapons;

internal class HeavyWeaponsMod : Mod
{
	public static HeavyWeaponsSettings settings;

	public static bool heavyWeaponsExist;

	public HeavyWeaponsMod(ModContentPack pack)
		: base(pack)
	{
		settings = ((Mod)this).GetSettings<HeavyWeaponsSettings>();
		BackwardsCompatibilityFixer.FixSettingsNameOrNamespace((Mod)(object)this, (ModSettings)(object)settings, "HeavyWeapons");
	}

	public override void DoSettingsWindowContents(Rect inRect)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		((Mod)this).DoSettingsWindowContents(inRect);
		settings.DoSettingsWindowContents(inRect);
	}

	public override string SettingsCategory()
	{
		if (heavyWeaponsExist)
		{
			return "Vanilla Weapons Expanded: Heavy";
		}
		return "";
	}

	public override void WriteSettings()
	{
		((Mod)this).WriteSettings();
		DefsAlterer.DoDefsAlter();
	}
}
