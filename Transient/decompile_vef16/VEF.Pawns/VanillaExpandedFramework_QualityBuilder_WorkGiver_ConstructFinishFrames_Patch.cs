using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace VEF.Pawns;

[HarmonyPatch]
public static class VanillaExpandedFramework_QualityBuilder_WorkGiver_ConstructFinishFrames_Patch
{
	public static MethodBase targetMethod;

	public static bool Prepare()
	{
		if (ModLister.AnyModActiveNoSuffix(new List<string>(1) { "hatti.qualitybuilder" }))
		{
			Type type = AccessTools.TypeByName("QualityBuilder._WorkGiver_ConstructFinishFrames");
			if (type != null)
			{
				targetMethod = AccessTools.Method(type, "Postfix", (Type[])null, (Type[])null);
				if (targetMethod != null)
				{
					return true;
				}
				Log.Error("[VEF] Failed to find target method for QualityBuilder WorkGiver_ConstructFinishFrames patch.");
				return false;
			}
			Log.Error("[VEF] Failed to find type for QualityBuilder WorkGiver_ConstructFinishFrames patch.");
		}
		return false;
	}

	public static MethodBase TargetMethod()
	{
		return targetMethod;
	}

	public static bool Prefix(Job __0)
	{
		if (__0?.workGiverDef?.giverClass != null && typeof(WorkGiver_ConstructionSkill_FinishFrames).IsAssignableFrom(__0.workGiverDef.giverClass))
		{
			return false;
		}
		return true;
	}
}
