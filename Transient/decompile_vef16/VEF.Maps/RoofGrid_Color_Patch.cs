using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class RoofGrid_Color_Patch
{
	private static Color baseColor = new Color(0.3f, 1f, 0.4f);

	private static bool Prepare(MethodBase method)
	{
		if (method != null)
		{
			return true;
		}
		if (ModLister.AnyModActiveNoSuffix(new List<string>(1) { "Mlie.ExpandedRoofing" }))
		{
			return false;
		}
		foreach (RoofDef allDef in DefDatabase<RoofDef>.AllDefs)
		{
			RoofExtension modExtension = ((Def)allDef).GetModExtension<RoofExtension>();
			if (modExtension != null && modExtension.EverUsesCustomOverlayColor)
			{
				return true;
			}
		}
		return false;
	}

	private static bool Prefix(ref Color __result)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		__result = Color.white;
		return false;
	}
}
