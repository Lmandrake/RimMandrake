using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Apparels;

public static class VanillaExpandedFramework_RunAndGun_Harmony_Verb_TryCastNextBurstShot
{
	public static class manual_SetStanceRunAndGun
	{
		public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
		{
			List<CodeInstruction> instructionList = instructions.ToList();
			MethodInfo shouldSetStanceInfo = AccessTools.Method(typeof(manual_SetStanceRunAndGun), "ShouldSetStance", (Type[])null, (Type[])null);
			for (int i = 0; i < instructionList.Count; i++)
			{
				CodeInstruction instruction = instructionList[i];
				if (instruction.opcode == OpCodes.Stloc_1)
				{
					yield return instruction;
					yield return new CodeInstruction(OpCodes.Ldloc_1, (object)null);
					yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
					yield return new CodeInstruction(OpCodes.Ldarg_1, (object)null);
					yield return new CodeInstruction(OpCodes.Call, (object)shouldSetStanceInfo);
					instruction = instruction.Clone();
				}
				yield return instruction;
			}
		}

		private static bool ShouldSetStance(bool original, Pawn_StanceTracker stanceTracker, Stance_Cooldown stance)
		{
			if (!original)
			{
				return stanceTracker.pawn.OffHandShield() == ((Stance_Busy)stance).verb.EquipmentSource;
			}
			return true;
		}
	}
}
