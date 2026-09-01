using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Apparels;

public static class VanillaExpandedFramework_DualWield_Harmony_FloatMenuMakerMap_AddHumanlikeOrders
{
	public static class manual_Postfix
	{
		public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
		{
			List<CodeInstruction> instructionList = instructions.ToList();
			MethodInfo getItemInfo = AccessTools.Method(typeof(List<Thing>), "get_Item", (Type[])null, (Type[])null);
			MethodInfo eligibleForDualWieldOptionInfo = AccessTools.Method(typeof(manual_Postfix), "EligibleForDualWieldOption", (Type[])null, (Type[])null);
			for (int i = 0; i < instructionList.Count; i++)
			{
				CodeInstruction val = instructionList[i];
				if (val.opcode == OpCodes.Ldloc_S && val.operand is LocalBuilder { LocalIndex: 12 })
				{
					yield return val;
					yield return new CodeInstruction(OpCodes.Ldloc_S, (object)10);
					yield return new CodeInstruction(OpCodes.Ldloc_S, (object)11);
					yield return new CodeInstruction(OpCodes.Callvirt, (object)getItemInfo);
					val = new CodeInstruction(OpCodes.Call, (object)eligibleForDualWieldOptionInfo);
				}
				yield return val;
			}
		}

		private static bool EligibleForDualWieldOption(bool result, Thing thing)
		{
			if (result && thing.def.IsShield())
			{
				return false;
			}
			return result;
		}
	}
}
