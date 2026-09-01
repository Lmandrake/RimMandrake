using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(HealthCardUtility), "GetPawnCapacityTip")]
public static class VanillaExpandedFramework_HealthCardUtility_GetPawnCapacityTip_Patch
{
	private static readonly List<Thing> tmpGearImpactors = new List<Thing>();

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr, MethodBase baseMethod)
	{
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Expected O, but got Unknown
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Expected O, but got Unknown
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Expected O, but got Unknown
		ConstructorInfo constructorInfo = AccessToolsExtensions.DeclaredConstructor(typeof(List<CapacityImpactor>), Array.Empty<Type>(), false);
		ConstructorInfo constructorInfo2 = AccessToolsExtensions.DeclaredConstructor(typeof(StringBuilder), Array.Empty<Type>(), false);
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[2]
		{
			new CodeMatch((OpCode?)OpCodes.Newobj, (object)constructorInfo, (string)null),
			CodeMatch.IsStloc((LocalBuilder)null)
		});
		int num = CodeInstructionExtensions.LocalIndex(val.Instruction);
		val.Reset(true);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[2]
		{
			new CodeMatch((OpCode?)OpCodes.Newobj, (object)constructorInfo2, (string)null),
			CodeMatch.IsStloc((LocalBuilder)null)
		});
		int num2 = CodeInstructionExtensions.LocalIndex(val.Instruction);
		val.End();
		val.Advance(-2);
		val.Insert((CodeInstruction[])(object)new CodeInstruction[4]
		{
			CodeInstruction.LoadArgument(GenCollection.FirstIndexOf<ParameterInfo>((IEnumerable<ParameterInfo>)baseMethod.GetParameters(), (Func<ParameterInfo, bool>)((ParameterInfo x) => x.ParameterType == typeof(Pawn))), false),
			CodeInstruction.LoadLocal(num, false),
			CodeInstruction.LoadLocal(num2, false),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<Action<Pawn, List<CapacityImpactor>, StringBuilder>>>)(() => InsertCustomImpactors))
		});
		return val.Instructions();
	}

	private static void InsertCustomImpactors(Pawn pawn, List<CapacityImpactor> list, StringBuilder sb)
	{
		if (pawn == null || sb == null || list == null || list.Count <= 0)
		{
			return;
		}
		for (int i = 0; i < list.Count; i++)
		{
			if (list[i] is CapacityImpactorGearMinLevel capacityImpactorGearMinLevel && !tmpGearImpactors.Contains(capacityImpactorGearMinLevel.gear))
			{
				sb.AppendLine("  " + ((CapacityImpactor)capacityImpactorGearMinLevel).Readable(pawn));
				tmpGearImpactors.Add(capacityImpactorGearMinLevel.gear);
			}
		}
		tmpGearImpactors.Clear();
	}
}
