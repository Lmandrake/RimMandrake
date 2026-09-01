using HarmonyLib;
using UnityEngine;
using VEF.Things;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(typeof(DeepResourceGrid), "GetCellExtraColor")]
public static class VanillaExpandedFramework_DeepResourceGrid_GetCellExtraColor
{
	[HarmonyPostfix]
	public static void PostFix(int index, DeepResourceGrid __instance, Map ___map, ref Color __result)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		IntVec3 val = ((CellIndices)(ref ___map.cellIndices)).IndexToCell(index);
		ThingDef val2 = __instance.ThingDefAt(val);
		ThingDefExtension modExtension = ((Def)val2).GetModExtension<ThingDefExtension>();
		if (modExtension != null)
		{
			float num = (float)__instance.CountAt(val) / (float)val2.deepCountPerCell * modExtension.transparencyMultiplier;
			__result = ColorExtension.ToTransparent(modExtension.deepColor, num);
		}
	}
}
