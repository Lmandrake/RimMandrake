using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class Furniture_Mod : Mod
{
	public Furniture_Mod(ModContentPack content)
		: base(content)
	{
		Furniture_Settings settings = ((Mod)this).GetSettings<Furniture_Settings>();
		BackwardsCompatibilityFixer.FixSettingsNameOrNamespace((Mod)(object)this, (ModSettings)(object)settings, "VanillaFurnitureExpanded", "VanillaFurnitureExpanded_Settings");
	}

	public override string SettingsCategory()
	{
		return "";
	}

	public override void DoSettingsWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		Furniture_Settings.DoWindowContents(inRect);
	}
}
