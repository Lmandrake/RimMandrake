using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class AnimalBehaviours_Mod : Mod
{
	public AnimalBehaviours_Mod(ModContentPack content)
		: base(content)
	{
		AnimalBehaviours_Settings settings = ((Mod)this).GetSettings<AnimalBehaviours_Settings>();
		BackwardsCompatibilityFixer.FixSettingsNameOrNamespace((Mod)(object)this, (ModSettings)(object)settings, "AnimalBehaviours");
	}

	public override string SettingsCategory()
	{
		return "Animal Behaviours";
	}

	public override void DoSettingsWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		AnimalBehaviours_Settings.DoWindowContents(inRect);
	}
}
