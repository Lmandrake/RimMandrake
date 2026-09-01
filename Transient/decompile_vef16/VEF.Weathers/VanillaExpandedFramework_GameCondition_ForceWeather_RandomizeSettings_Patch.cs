using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weathers;

[HarmonyPatch]
public static class VanillaExpandedFramework_GameCondition_ForceWeather_RandomizeSettings_Patch
{
	[HarmonyTargetMethods]
	public static IEnumerable<MethodInfo> TargetMethods()
	{
		return new MethodInfo[2]
		{
			AccessTools.Method(typeof(CompCauseGameCondition_ForceWeather), "RandomizeSettings", (Type[])null, (Type[])null),
			AccessTools.Method(typeof(GameCondition_ForceWeather), "RandomizeSettings", (Type[])null, (Type[])null)
		}.SelectMany(GetFilters);
	}

	private static IEnumerable<MethodInfo> GetFilters(MethodInfo from)
	{
		return from instruction in PatchProcessor.GetOriginalInstructions((MethodBase)@from, (ILGenerator)null)
			where instruction.opcode == OpCodes.Ldftn
			select (MethodInfo)instruction.operand;
	}

	[HarmonyPostfix]
	public static void Postfix(WeatherDef __0, ref bool __result)
	{
		if (__result)
		{
			WeatherExtension weatherExtension = ((__0 != null) ? ((Def)__0).GetModExtension<WeatherExtension>() : null);
			if (weatherExtension != null && !weatherExtension.canRandomlyGenerate)
			{
				__result = false;
			}
		}
	}
}
