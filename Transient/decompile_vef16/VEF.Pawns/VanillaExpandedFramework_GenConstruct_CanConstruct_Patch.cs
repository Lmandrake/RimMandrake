using System;
using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(GenConstruct), "CanConstruct", new Type[]
{
	typeof(Thing),
	typeof(Pawn),
	typeof(WorkTypeDef),
	typeof(bool),
	typeof(JobDef)
})]
public static class VanillaExpandedFramework_GenConstruct_CanConstruct_Patch
{
	public static void Prefix(Thing t, Pawn pawn, ref WorkTypeDef workType, bool forced = false)
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
		if (thingDefExtension?.constructionSkillRequirement != null)
		{
			workType = thingDefExtension.constructionSkillRequirement.workType;
		}
	}
}
