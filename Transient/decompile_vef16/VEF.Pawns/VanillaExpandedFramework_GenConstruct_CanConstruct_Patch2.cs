using System;
using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;
using Verse.AI;

namespace VEF.Pawns;

[HarmonyPatch(typeof(GenConstruct), "CanConstruct", new Type[]
{
	typeof(Thing),
	typeof(Pawn),
	typeof(bool),
	typeof(bool),
	typeof(JobDef)
})]
public static class VanillaExpandedFramework_GenConstruct_CanConstruct_Patch2
{
	public static bool Prefix(ref bool __result, Thing t, Pawn p, ref bool checkSkills, bool forced)
	{
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
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
		if (thingDefExtension?.constructionSkillRequirement != null && p.skills != null && p.skills.GetSkill(thingDefExtension.constructionSkillRequirement.skill).Level < thingDefExtension.constructionSkillRequirement.level)
		{
			JobFailReason.Is(TaggedString.op_Implicit(GrammarResolverSimpleStringExtensions.Formatted(Translator.Translate("SkillTooLowForConstruction"), NamedArgument.op_Implicit(((Def)thingDefExtension.constructionSkillRequirement.skill).LabelCap))), (string)null);
			__result = false;
			return false;
		}
		return true;
	}
}
