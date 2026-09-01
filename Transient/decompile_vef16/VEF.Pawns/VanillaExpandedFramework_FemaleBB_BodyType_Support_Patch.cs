using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using VEF.Apparels;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch]
public static class VanillaExpandedFramework_FemaleBB_BodyType_Support_Patch
{
	private static MethodBase target;

	private static bool Prepare()
	{
		if (ModLister.AnyModActiveNoSuffix(new List<string>(1) { "ssulunge.BBBodySupport" }))
		{
			Type type = AccessTools.TypeByName("BBBodySupport.BBBodyTypeSupportHarmony+BBBodyGraphicApparelPatch");
			if (type == null)
			{
				Log.Error("[VEF] Failed to find BBBodySupport.BBBodyTypeSupportHarmony+BBBodyGraphicApparelPatch type.");
				return false;
			}
			target = AccessTools.Method(type, "BBBody_GraphicApparelPatch", (Type[])null, (Type[])null);
			if (target == null)
			{
				Log.Error("[VEF] Failed to find BBBody_GraphicApparelPatch method in BBBodySupport.BBBodyTypeSupportHarmony+BBBodyGraphicApparelPatch type.");
				return false;
			}
			return true;
		}
		return false;
	}

	[HarmonyTargetMethod]
	public static MethodBase GetMethod()
	{
		return target;
	}

	public static bool Prefix(ref Apparel apparel, ref BodyTypeDef bodyType, ref ApparelGraphicRecord rec, ref bool __3, ref bool __result)
	{
		if (VanillaExpandedFramework_ApparelGraphicRecordGetter_TryGetGraphicApparel_Transpiler.IsUnifiedApparel(apparel))
		{
			__3 = true;
			__result = true;
			return false;
		}
		return true;
	}
}
