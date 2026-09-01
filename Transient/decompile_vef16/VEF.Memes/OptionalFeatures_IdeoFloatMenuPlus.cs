using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;

namespace VEF.Memes;

public static class OptionalFeatures_IdeoFloatMenuPlus
{
	public static void ApplyFeature(Harmony harm)
	{
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Expected O, but got Unknown
		harm.Patch((MethodBase)AccessTools.Method(typeof(IdeoUIUtility), "AddPrecept", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_IdeoUIUtility_AddPrecept_Patch), "Transpiler", (Type[])null), (HarmonyMethod)null);
	}
}
