using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(DamageWorker_AddInjury), "ApplyToPawn")]
public static class VanillaExpandedFramework__DamageWorker_AddInjury_ApplyToPawn_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		AccessTools.Field(typeof(FleshTypeDef), "damageEffecter");
		MethodInfo getEffecterDef = AccessTools.Method(typeof(VanillaExpandedFramework__DamageWorker_AddInjury_ApplyToPawn_Patch), "GetEffecterDef", (Type[])null, (Type[])null);
		foreach (CodeInstruction codeInstruction in codeInstructions)
		{
			yield return codeInstruction;
			if (codeInstruction.opcode == OpCodes.Stloc_S && codeInstruction.operand is LocalBuilder { LocalIndex: 11 })
			{
				yield return new CodeInstruction(OpCodes.Ldloc_S, (object)11);
				yield return new CodeInstruction(OpCodes.Ldarg_2, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)getEffecterDef);
				yield return new CodeInstruction(OpCodes.Stloc_S, (object)11);
			}
		}
	}

	public static EffecterDef GetEffecterDef(EffecterDef effecterDef, Pawn curPawn)
	{
		if (curPawn != null && StaticCollectionsClass.bloodEffect_gene_pawns.ContainsKey((Thing)(object)curPawn))
		{
			return StaticCollectionsClass.bloodEffect_gene_pawns[(Thing)(object)curPawn];
		}
		return effecterDef;
	}
}
