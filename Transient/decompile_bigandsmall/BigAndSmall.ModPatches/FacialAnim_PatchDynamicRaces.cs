using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace BigAndSmall.ModPatches;

public static class FacialAnim_PatchDynamicRaces
{
	public static void PatchFaceAdjustmentDict(List<ThingDef> racesToAdd)
	{
		if (!ModsConfig.IsActive("Nals.FacialAnimation"))
		{
			return;
		}
		object value = AccessTools.Field(AccessTools.TypeByName("FacialAnimation.GraphicHelper"), "faceAdjustmentDict").GetValue(null);
		object value2 = AccessTools.Field(AccessTools.TypeByName("FacialAnimation.FaceAdjustmentDefOf"), "DefaultFaceSizeAndPositionDef").GetValue(null);
		PropertyInfo property = value.GetType().GetProperty("Item");
		foreach (ThingDef item in racesToAdd)
		{
			property.SetValue(value, value2, new object[1] { ((Def)item).defName });
		}
	}
}
