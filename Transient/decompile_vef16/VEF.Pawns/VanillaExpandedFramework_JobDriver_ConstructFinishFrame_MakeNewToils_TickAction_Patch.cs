using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;
using Verse.AI;

namespace VEF.Pawns;

[HarmonyPatch]
public static class VanillaExpandedFramework_JobDriver_ConstructFinishFrame_MakeNewToils_TickAction_Patch
{
	[HarmonyTargetMethod]
	public static MethodBase TargetMethod()
	{
		return typeof(JobDriver_ConstructFinishFrame).GetNestedTypes(AccessTools.all).SelectMany((Type x) => from x in x.GetMethods(AccessTools.all)
			where x.Name.Contains("<MakeNewToils>") && x.ReturnType == typeof(void)
			select x).ToList()[1];
	}

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions, MethodBase method)
	{
		FieldInfo constructionField = AccessTools.Field(typeof(SkillDefOf), "Construction");
		MethodInfo interceptSkillInfo = AccessTools.Method(typeof(VanillaExpandedFramework_JobDriver_ConstructFinishFrame_MakeNewToils_TickAction_Patch), "InterceptSkill", (Type[])null, (Type[])null);
		MethodInfo shouldSkipCheckInfo = AccessTools.Method(typeof(VanillaExpandedFramework_JobDriver_ConstructFinishFrame_MakeNewToils_TickAction_Patch), "ShouldSkipCheck", (Type[])null, (Type[])null);
		FieldInfo thisField = method.DeclaringType.GetField("<>4__this");
		List<CodeInstruction> codes = codeInstructions.ToList();
		bool patched = false;
		for (int i = 0; i < codes.Count; i++)
		{
			CodeInstruction code = codes[i];
			yield return code;
			if (CodeInstructionExtensions.LoadsField(code, constructionField, false))
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)thisField);
				yield return new CodeInstruction(OpCodes.Call, (object)interceptSkillInfo);
			}
			if (!patched && code.opcode == OpCodes.Bge_Un_S)
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)thisField);
				yield return new CodeInstruction(OpCodes.Call, (object)shouldSkipCheckInfo);
				yield return new CodeInstruction(OpCodes.Brtrue_S, code.operand);
				patched = true;
			}
		}
	}

	public static bool ShouldSkipCheck(JobDriver_ConstructFinishFrame jobDriver)
	{
		Thing thing = ((LocalTargetInfo)(ref ((JobDriver)jobDriver).job.targetA)).Thing;
		object obj;
		if (thing == null)
		{
			obj = null;
		}
		else
		{
			ThingDef def = thing.def;
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
		if (((ThingDefExtension)obj)?.constructionSkillRequirement != null)
		{
			return true;
		}
		return false;
	}

	public static SkillDef InterceptSkill(SkillDef skillDef, JobDriver_ConstructFinishFrame jobDriver)
	{
		Thing thing = ((LocalTargetInfo)(ref ((JobDriver)jobDriver).job.targetA)).Thing;
		object obj;
		if (thing == null)
		{
			obj = null;
		}
		else
		{
			ThingDef def = thing.def;
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
			return thingDefExtension.constructionSkillRequirement.skill;
		}
		return skillDef;
	}
}
