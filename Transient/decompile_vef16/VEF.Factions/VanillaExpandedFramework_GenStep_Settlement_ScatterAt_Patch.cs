using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(GenStep_Settlement), "ScatterAt")]
public static class VanillaExpandedFramework_GenStep_Settlement_ScatterAt_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		List<CodeInstruction> instructionList = instructions.ToList();
		MethodInfo settlementGenerationSymbolInfo = AccessTools.Method(typeof(VanillaExpandedFramework_GenStep_Settlement_ScatterAt_Patch), "SettlementGenerationSymbol", (Type[])null, (Type[])null);
		for (int i = 0; i < instructionList.Count; i++)
		{
			CodeInstruction val = instructionList[i];
			if (val.opcode == OpCodes.Ldstr && (string)val.operand == "settlement")
			{
				yield return val;
				yield return CodeInstruction.LoadLocal(4, false);
				val = new CodeInstruction(OpCodes.Call, (object)settlementGenerationSymbolInfo);
			}
			yield return val;
		}
	}

	private static string SettlementGenerationSymbol(string original, Faction faction)
	{
		return FactionDefExtension.Get((Def)(object)faction.def).settlementGenerationSymbol ?? original;
	}
}
