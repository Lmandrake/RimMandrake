using HarmonyLib;
using Verse;

namespace VEF.Weathers;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_WeatherWorker_Constructor_Patch
{
	public static void Postfix(WeatherWorker __instance, WeatherDef def)
	{
		if (__instance.overlays == null)
		{
			return;
		}
		for (int num = __instance.overlays.Count - 1; num >= 0; num--)
		{
			if (__instance.overlays[num] is WeatherOverlay_Custom)
			{
				__instance.overlays[num] = (SkyOverlay)(object)new WeatherOverlay_Custom
				{
					weatherDef = def
				};
			}
		}
	}
}
