using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

[HarmonyPatch(typeof(JobDriver_Wait), "CheckForAutoAttack")]
public static class VanillaExpandedFramework_JobDriver_Wait_CheckForAutoAttack_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator generator)
	{
		List<CodeInstruction> codes = instructions.ToList();
		Label label = generator.DefineLabel();
		for (int i = 0; i < codes.Count; i++)
		{
			if (codes[i].opcode == OpCodes.Brtrue_S && CodeInstructionExtensions.Calls(codes[i - 1], AccessTools.Method(typeof(VerbProperties), "get_IsMeleeAttack", (Type[])null, (Type[])null)))
			{
				codes[i + 1].labels.Add(label);
				yield return new CodeInstruction(OpCodes.Brfalse_S, (object)label);
				yield return new CodeInstruction(OpCodes.Ldloc_S, (object)9);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(MeleeReachCombatUtility), "IsVanillaMeleeAttack", (Type[])null, (Type[])null));
				yield return new CodeInstruction(OpCodes.Brtrue_S, codes[i].operand);
			}
			else
			{
				yield return codes[i];
			}
		}
	}
}
