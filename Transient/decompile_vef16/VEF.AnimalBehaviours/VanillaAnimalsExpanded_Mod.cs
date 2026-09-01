using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class VanillaAnimalsExpanded_Mod : Mod
{
	public static VanillaAnimalsExpanded_Settings settings;

	public VanillaAnimalsExpanded_Mod(ModContentPack content)
		: base(content)
	{
		settings = ((Mod)this).GetSettings<VanillaAnimalsExpanded_Settings>();
		BackwardsCompatibilityFixer.FixSettingsNameOrNamespace((Mod)(object)this, (ModSettings)(object)settings, "AnimalBehaviours");
	}

	public override string SettingsCategory()
	{
		if (DefDatabase<GenericToggleableAnimalDef>.AllDefsListForReading.Select((GenericToggleableAnimalDef k) => k).Any())
		{
			return "Animal Toggles";
		}
		return "";
	}

	public override void DoSettingsWindowContents(Rect inRect)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		((Mod)this).DoSettingsWindowContents(inRect);
		foreach (GenericToggleableAnimalDef item in DefDatabase<GenericToggleableAnimalDef>.AllDefsListForReading.Select((GenericToggleableAnimalDef k) => k).ToList())
		{
			if (settings.pawnSpawnStates == null)
			{
				settings.pawnSpawnStates = new Dictionary<string, bool>();
			}
			foreach (string toggleablePawn in item.toggleablePawns)
			{
				if (!settings.pawnSpawnStates.ContainsKey(toggleablePawn) && DefDatabase<ThingDef>.GetNamedSilentFail(toggleablePawn) != null)
				{
					settings.pawnSpawnStates[toggleablePawn] = false;
				}
			}
		}
		settings.DoWindowContents(inRect);
	}
}
