using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weathers;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_WeatherManager_CurWeatherPerceived_Patch
{
	private static readonly Dictionary<Map, WeatherDef> weathers = new Dictionary<Map, WeatherDef>();

	private static void Postfix(WeatherManager __instance, WeatherDef __result)
	{
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		if (weathers.TryGetValue(__instance.map, out var value) && __result != value)
		{
			weathers[__instance.map] = __result;
			WeatherLetterExtensions modExtension = ((Def)__result).GetModExtension<WeatherLetterExtensions>();
			if (modExtension != null)
			{
				Find.LetterStack.ReceiveLetter(TaggedString.op_Implicit(modExtension.letterTitle), TaggedString.op_Implicit(modExtension.letterText), modExtension.letterDef, (string)null, 0, true);
			}
		}
		else
		{
			weathers[__instance.map] = __result;
		}
	}
}
