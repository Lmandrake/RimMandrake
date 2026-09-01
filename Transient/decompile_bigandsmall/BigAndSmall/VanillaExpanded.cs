using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

public static class VanillaExpanded
{
	private static bool? _veActive;

	private static bool? _veHActive;

	/// <summary>
	/// Checks if Vanlla Expanded is loaded.
	/// </summary>
	public static bool VEActive
	{
		get
		{
			bool valueOrDefault = _veActive == true;
			if (!_veActive.HasValue)
			{
				valueOrDefault = ModsConfig.IsActive("OskarPotocki.VanillaFactionsExpanded.Core");
				_veActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static bool VEHighMatesActive
	{
		get
		{
			bool valueOrDefault = _veHActive == true;
			if (!_veHActive.HasValue)
			{
				valueOrDefault = ModsConfig.IsActive("vanillaracesexpanded.highmate");
				_veHActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static void PatchVanillaExpanded(Harmony harmony)
	{
		if (VEHighMatesActive)
		{
			PatchVEHToils(harmony);
		}
	}

	public static void PatchVEHToils(Harmony harmony)
	{
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Expected O, but got Unknown
		MethodBase methodBase = AccessTools.Method("VanillaRacesExpandedHighmate.JobDriver_InitiateLovin:MakeNewToils", (Type[])null, (Type[])null);
		HarmonyMethod val = new HarmonyMethod(typeof(LovinPatches).GetMethod("VEHighmates_Lovin", BindingFlags.Static | BindingFlags.Public));
		harmony.Patch(methodBase, (HarmonyMethod)null, val, (HarmonyMethod)null, (HarmonyMethod)null);
	}
}
