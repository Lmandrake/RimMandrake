using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(Frame), "CompleteConstruction")]
public static class VanillaExpandedFramework_Frame_CompleteConstruction_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		FieldInfo constructionField = AccessTools.Field(typeof(SkillDefOf), "Construction");
		MethodInfo interceptSkillInfo = AccessTools.Method(typeof(VanillaExpandedFramework_Frame_CompleteConstruction_Patch), "InterceptSkill", (Type[])null, (Type[])null);
		foreach (CodeInstruction instruction in codeInstructions)
		{
			yield return instruction;
			if (CodeInstructionExtensions.LoadsField(instruction, constructionField, false))
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)interceptSkillInfo);
			}
		}
	}

	public static SkillDef InterceptSkill(SkillDef skillDef, Frame frame)
	{
		object obj;
		if (frame == null)
		{
			obj = null;
		}
		else
		{
			ThingDef def = ((Thing)frame).def;
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
