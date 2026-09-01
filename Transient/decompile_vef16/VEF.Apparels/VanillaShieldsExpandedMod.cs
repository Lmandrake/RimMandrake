using UnityEngine;
using Verse;

namespace VEF.Apparels;

public class VanillaShieldsExpandedMod : Mod
{
	public static VanillaShieldsExpandedSettings settings;

	public VanillaShieldsExpandedMod(ModContentPack pack)
		: base(pack)
	{
		settings = ((Mod)this).GetSettings<VanillaShieldsExpandedSettings>();
		BackwardsCompatibilityFixer.FixSettingsNameOrNamespace((Mod)(object)this, (ModSettings)(object)settings);
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
		if (!VanillaShieldsExpandedStartup.anyShieldItemPresent)
		{
			return "";
		}
		return "Vanilla Shields Expanded";
	}

	public override void WriteSettings()
	{
		((Mod)this).WriteSettings();
		VanillaShieldsExpandedStartup.SetValues();
	}
}
