using System.Collections.Generic;
using VEF.Weathers;
using Verse;

namespace VEF;

[StaticConstructorOnStartup]
public static class ModSettingsHandler
{
	static ModSettingsHandler()
	{
		VFEGlobalSettings settings = VFEGlobal.settings;
		if (settings.weatherDamagesOptions == null)
		{
			settings.weatherDamagesOptions = new Dictionary<string, bool>();
		}
		foreach (WeatherDef allDef in DefDatabase<WeatherDef>.AllDefs)
		{
			if (((Def)allDef).GetModExtension<WeatherEffectsExtension>() != null && !VFEGlobal.settings.weatherDamagesOptions.ContainsKey(((Def)allDef).defName))
			{
				VFEGlobal.settings.weatherDamagesOptions[((Def)allDef).defName] = true;
			}
		}
	}
}
