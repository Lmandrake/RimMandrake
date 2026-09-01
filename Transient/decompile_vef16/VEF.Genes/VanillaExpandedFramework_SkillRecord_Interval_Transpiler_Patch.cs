using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch]
public static class VanillaExpandedFramework_SkillRecord_Interval_Transpiler_Patch
{
	private static MethodBase TargetMethod()
	{
		return AccessTools.Method(typeof(SkillRecord), "Interval", (Type[])null, (Type[])null);
	}

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		FieldInfo pawn = AccessTools.Field(typeof(SkillRecord), "pawn");
		foreach (CodeInstruction instruction in instructions)
		{
			yield return instruction;
			if (instruction.opcode == OpCodes.Stloc_0)
			{
				yield return new CodeInstruction(OpCodes.Ldloc_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)pawn);
				yield return CodeInstruction.Call(typeof(VanillaExpandedFramework_SkillRecord_Interval_Transpiler_Patch), "GetMultiplier", (Type[])null, (Type[])null);
				yield return new CodeInstruction(OpCodes.Mul, (object)null);
				yield return new CodeInstruction(OpCodes.Stloc_0, (object)null);
			}
		}
	}

	public static float GetMultiplier(Pawn pawn)
	{
		if (StaticCollectionsClass.skillLossMultiplier_gene_pawns.ContainsKey((Thing)(object)pawn))
		{
			return StaticCollectionsClass.skillLossMultiplier_gene_pawns[(Thing)(object)pawn];
		}
		return 1f;
	}
}
