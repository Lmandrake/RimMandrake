using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(typeof(RoofGrid), "GetCellExtraColor")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_RoofGrid_GetCellExtraColor_Patch
{
	private static bool expandedRoofingActive = false;

	private static Color baseColor = new Color(0.3f, 1f, 0.4f);

	private static bool Prepare(MethodBase method)
	{
		if (method != null)
		{
			return true;
		}
		expandedRoofingActive = ModLister.AnyModActiveNoSuffix(new List<string>(1) { "Mlie.ExpandedRoofing" });
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

	private static void Postfix(int index, RoofDef[] ___roofGrid, Map ___map, ref Color __result)
	{
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		RoofDef val = ___roofGrid[index];
		Color? val2 = ((val == null) ? ((Color?)null) : ((Def)val).GetModExtension<RoofExtension>()?.RoofOverlayColor(___map, index, val));
		if (val2.HasValue)
		{
			Color valueOrDefault = val2.GetValueOrDefault();
			__result = valueOrDefault;
		}
		else if (!expandedRoofingActive)
		{
			__result *= baseColor;
		}
	}
}
