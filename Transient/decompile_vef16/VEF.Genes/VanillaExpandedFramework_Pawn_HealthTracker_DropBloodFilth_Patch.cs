using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(Pawn_HealthTracker), "DropBloodFilth")]
public static class VanillaExpandedFramework_Pawn_HealthTracker_DropBloodFilth_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo TryChangeBloodFilthInfo = AccessTools.Method(typeof(VanillaExpandedFramework_Pawn_HealthTracker_DropBloodFilth_Patch), "TryChangeBloodFilth", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			if (i == 0)
			{
				yield return codes[i];
			}
			else if (codes[i].opcode == OpCodes.Ldloc_0 && codes[i - 1].opcode == OpCodes.Callvirt)
			{
				yield return new CodeInstruction(OpCodes.Ldloc_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)AccessTools.Field(typeof(Pawn_HealthTracker), "pawn"));
				yield return new CodeInstruction(OpCodes.Call, (object)TryChangeBloodFilthInfo);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static ThingDef TryChangeBloodFilth(ThingDef thingDef, Pawn pawn)
	{
		if (StaticCollectionsClass.bloodtype_gene_pawns.TryGetValue((Thing)(object)pawn, out var value))
		{
			return value;
		}
		return thingDef;
	}
}
