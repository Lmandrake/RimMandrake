using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(Pawn_HealthTracker), "DropBloodSmear")]
public static class VanillaExpandedFramework_Pawn_HealthTracker_DropBloodSmear_Patch
{
	public static MethodInfo TryChangeBloodSmearInfo = AccessTools.Method(typeof(VanillaExpandedFramework_Pawn_HealthTracker_DropBloodSmear_Patch), "TryChangeBloodSmear", (Type[])null, (Type[])null);

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		foreach (CodeInstruction code in codeInstructions)
		{
			yield return code;
			if (code.opcode == OpCodes.Stloc_0)
			{
				yield return new CodeInstruction(OpCodes.Ldloc_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)AccessTools.Field(typeof(Pawn_HealthTracker), "pawn"));
				yield return new CodeInstruction(OpCodes.Call, (object)TryChangeBloodSmearInfo);
				yield return new CodeInstruction(OpCodes.Stloc_0, (object)null);
			}
		}
	}

	public static ThingDef TryChangeBloodSmear(ThingDef thingDef, Pawn pawn)
	{
		if (StaticCollectionsClass.bloodsmear_gene_pawns.TryGetValue((Thing)(object)pawn, out var value))
		{
			return value;
		}
		return thingDef;
	}
}
