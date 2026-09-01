using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch]
public static class Workgiver_Patches
{
	[HarmonyTargetMethods]
	public static IEnumerable<MethodBase> TargetMethods()
	{
		yield return AccessTools.Method(typeof(WorkGiver_ConstructDeliverResourcesToBlueprints), "JobOnThing", (Type[])null, (Type[])null);
		yield return AccessTools.Method(typeof(WorkGiver_ConstructDeliverResourcesToFrames), "JobOnThing", (Type[])null, (Type[])null);
		yield return AccessTools.Method(typeof(WorkGiver_ConstructFinishFrames), "JobOnThing", (Type[])null, (Type[])null);
		yield return AccessTools.DeclaredMethod(typeof(WorkGiver_ConstructDeliverResourcesToBlueprints), "HasJobOnThing", (Type[])null, (Type[])null);
		yield return AccessTools.DeclaredMethod(typeof(WorkGiver_ConstructDeliverResourcesToFrames), "HasJobOnThing", (Type[])null, (Type[])null);
	}

	public static bool Prefix(WorkGiver __instance, Pawn pawn, Thing t)
	{
		object obj;
		if (t == null)
		{
			obj = null;
		}
		else
		{
			ThingDef def = t.def;
			if (def == null)
			{
				obj = null;
			}
			else
			{
				BuildableDef entityDefToBuild = def.entityDefToBuild;
				obj = ((entityDefToBuild != null) ? ((Def)entityDefToBuild).GetModExtension<ThingDefExtension>() : null);
			}
		}
		ThingDefExtension thingDefExtension = (ThingDefExtension)obj;
		if (thingDefExtension?.constructionSkillRequirement != null && __instance.def?.workType != null && __instance.def.workType != thingDefExtension.constructionSkillRequirement.workType)
		{
			return false;
		}
		return true;
	}
}
