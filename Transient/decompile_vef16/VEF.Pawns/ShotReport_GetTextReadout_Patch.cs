using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(ShotReport), "GetTextReadout")]
public static class ShotReport_GetTextReadout_Patch
{
	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Expected O, but got Unknown
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Expected O, but got Unknown
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Expected O, but got Unknown
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Expected O, but got Unknown
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Expected O, but got Unknown
		//IL_01d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01de: Expected O, but got Unknown
		MethodInfo methodInfo = AccessToolsExtensions.DeclaredPropertyGetter(typeof(ShotReport), "TotalEstimatedHitChance");
		MethodInfo methodInfo2 = AccessToolsExtensions.DeclaredPropertyGetter(typeof(ShotReport), "FactorFromPosture");
		FieldInfo fieldInfo = AccessToolsExtensions.DeclaredField(typeof(ShotReport), "target");
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchStartForward((CodeMatch[])(object)new CodeMatch[6]
		{
			CodeMatch.IsLdloc((LocalBuilder)null),
			CodeMatch.IsLdarg((int?)0),
			CodeMatch.Calls(methodInfo),
			new CodeMatch((OpCode?)OpCodes.Call, (object)null, (string)null),
			new CodeMatch((OpCode?)OpCodes.Callvirt, (object)null, (string)null),
			new CodeMatch((OpCode?)OpCodes.Pop, (object)null, (string)null)
		});
		val.Advance(3);
		val.Insert((CodeInstruction[])(object)new CodeInstruction[3]
		{
			CodeInstruction.LoadArgument(0, false),
			new CodeInstruction(OpCodes.Ldflda, (object)fieldInfo),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<_003C_003EF_007B00000008_007D<float, TargetInfo, float>>>)(() => AddDodgeToTotalEstimate))
		});
		val.Start();
		val.MatchStartForward((CodeMatch[])(object)new CodeMatch[4]
		{
			CodeMatch.IsLdarg((int?)0),
			CodeMatch.Calls(methodInfo2),
			CodeMatch.LoadsConstant(0.9998999834060669),
			CodeMatch.Branches((string)null)
		});
		val.Insert((CodeInstruction[])(object)new CodeInstruction[4]
		{
			CodeInstructionExtensions.MoveLabelsFrom(CodeInstruction.LoadLocal(0, false), val.Instruction),
			CodeInstruction.LoadArgument(0, false),
			new CodeInstruction(OpCodes.Ldflda, (object)fieldInfo),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<_003C_003EA_007B00000008_007D<StringBuilder, TargetInfo>>>)(() => AddDodgeChanceText))
		});
		return val.Instructions();
	}

	private static float AddDodgeToTotalEstimate(float currentEstimate, ref TargetInfo target)
	{
		Thing thing = ((TargetInfo)(ref target)).Thing;
		if (thing == null)
		{
			return currentEstimate;
		}
		float statValue = StatExtension.GetStatValue(thing, InternalDefOf.VEF_RangedDodgeChance, true, -1);
		if (statValue <= 0f)
		{
			return currentEstimate;
		}
		return Mathf.Clamp01(currentEstimate * (1f - statValue));
	}

	private static void AddDodgeChanceText(StringBuilder builder, ref TargetInfo target)
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		Thing thing = ((TargetInfo)(ref target)).Thing;
		if (thing != null)
		{
			float statValue = StatExtension.GetStatValue(thing, InternalDefOf.VEF_RangedDodgeChance, true, -1);
			if (statValue > 0f)
			{
				builder.AppendLine(string.Format("   {0}: {1}", Translator.Translate("VEF.RangedDodge.ShotReportReadout"), GenText.ToStringPercent(Mathf.Clamp01(1f - statValue))));
			}
		}
	}
}
