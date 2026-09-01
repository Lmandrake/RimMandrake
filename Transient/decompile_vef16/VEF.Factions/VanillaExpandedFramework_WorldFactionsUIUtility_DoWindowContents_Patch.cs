using System;
using System.Collections.Generic;
using System.Reflection.Emit;
using System.Text;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(WorldFactionsUIUtility), "DoWindowContents")]
public static class VanillaExpandedFramework_WorldFactionsUIUtility_DoWindowContents_Patch
{
	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instructions, (ILGenerator)null);
		CodeInstruction instruction = val.MatchEndForward((CodeMatch[])(object)new CodeMatch[2]
		{
			new CodeMatch((OpCode?)OpCodes.Newobj, (object)AccessTools.DeclaredConstructor(typeof(StringBuilder), Array.Empty<Type>(), false), (string)null),
			CodeMatch.StoresLocal((string)null)
		}).Instruction;
		int num = ((instruction.operand is LocalBuilder localBuilder) ? localBuilder.LocalIndex : CodeInstructionExtensions.LocalIndex(instruction));
		val.MatchStartForward((CodeMatch[])(object)new CodeMatch[2]
		{
			CodeMatch.LoadsLocal(false, (string)null),
			CodeMatch.Calls(AccessTools.PropertyGetter(typeof(StringBuilder), "Length"))
		}).Insert((CodeInstruction[])(object)new CodeInstruction[3]
		{
			CodeInstruction.LoadArgument(1, false),
			CodeInstruction.LoadLocal(num, false),
			CodeInstruction.Call(typeof(VanillaExpandedFramework_WorldFactionsUIUtility_DoWindowContents_Patch), "InsertFactionWarnings", (Type[])null, (Type[])null)
		});
		return val.Instructions();
	}

	private static void InsertFactionWarnings(List<FactionDef> activeFactions, StringBuilder builder)
	{
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		bool flag = GenCollection.Count<FactionDef>(activeFactions, (Predicate<FactionDef>)((FactionDef x) => !x.hidden)) != 0;
		foreach (FactionDef configurableFaction in FactionGenerator.ConfigurableFactions)
		{
			ForcedFactionData forcedFactionData = FactionDefExtension.Get((Def)(object)configurableFaction).forcedFactionData;
			if (!forcedFactionData.preventRemovalAtWorldGeneration && (flag || forcedFactionData.displayMissingWarningIfNoFactionPresent) && forcedFactionData.UnderRequiredWorldGenFactionCount(configurableFaction, activeFactions))
			{
				builder.AppendLine(TaggedString.op_Implicit(forcedFactionData.GetWorldGenMissingFactionMessage(configurableFaction, activeFactions)));
			}
		}
	}
}
