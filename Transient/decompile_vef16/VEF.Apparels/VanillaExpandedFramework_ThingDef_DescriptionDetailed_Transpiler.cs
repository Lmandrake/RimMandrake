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

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_ThingDef_DescriptionDetailed_Transpiler
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Expected O, but got Unknown
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Expected O, but got Unknown
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Expected O, but got Unknown
		ConstructorInfo constructorInfo = AccessToolsExtensions.Constructor(typeof(StringBuilder), Array.Empty<Type>(), false);
		MethodInfo methodInfo = AccessToolsExtensions.Method(typeof(object), "ToString", (Type[])null, (Type[])null);
		CodeMatcher val = new CodeMatcher(instructions, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[2]
		{
			new CodeMatch((OpCode?)OpCodes.Newobj, (object)constructorInfo, (string)null),
			CodeMatch.IsStloc((LocalBuilder)null)
		});
		int num = CodeInstructionExtensions.LocalIndex(val.Instruction);
		val.MatchStartForward((CodeMatch[])(object)new CodeMatch[4]
		{
			CodeMatch.IsLdarg((int?)null),
			CodeMatch.IsLdloc((LocalBuilder)null),
			CodeMatch.Calls(methodInfo),
			new CodeMatch((OpCode?)OpCodes.Stfld, (object)null, (string)null)
		});
		val.Insert((CodeInstruction[])(object)new CodeInstruction[3]
		{
			CodeInstructionExtensions.MoveLabelsFrom(CodeInstruction.LoadLocal(num, false), val.Instruction),
			CodeInstruction.LoadArgument(0, false),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<Action<StringBuilder, ThingDef>>>)(() => ModifyValue))
		});
		return val.Instructions();
	}

	public static void ModifyValue(StringBuilder stringBuilder, ThingDef thingDef)
	{
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		if (!thingDef.IsApparel)
		{
			return;
		}
		ApparelExtension modExtension = ((Def)thingDef).GetModExtension<ApparelExtension>();
		if (modExtension == null || GenList.NullOrEmpty<StatModifier>((IList<StatModifier>)modExtension.equippedStatFactors))
		{
			return;
		}
		bool flag = !GenList.NullOrEmpty<StatModifier>((IList<StatModifier>)thingDef.equippedStatOffsets);
		if (!flag)
		{
			stringBuilder.AppendLine();
			stringBuilder.AppendLine();
		}
		for (int i = 0; i < modExtension.equippedStatFactors.Count; i++)
		{
			if (i > 0 || flag)
			{
				stringBuilder.AppendLine();
			}
			StatModifier val = modExtension.equippedStatFactors[i];
			stringBuilder.Append($"{((Def)val.stat).LabelCap}: {val.stat.Worker.ValueToString(val.value, false, (ToStringNumberSense)2)}");
		}
	}
}
