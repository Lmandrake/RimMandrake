using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(StatWorker), "GetOffsetsAndFactorsExplanation")]
public static class VanillaExpandedFramework_StatWorker_GetOffsetsAndFactorsExplanation_Transpiler
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Expected O, but got Unknown
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Expected O, but got Unknown
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Expected O, but got Unknown
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Expected O, but got Unknown
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0139: Expected O, but got Unknown
		//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b8: Expected O, but got Unknown
		//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f1: Expected O, but got Unknown
		MethodInfo methodInfo = AccessToolsExtensions.DeclaredMethod(typeof(StatWorker), "InfoTextLineFromGear", (Type[])null, (Type[])null);
		MethodInfo methodInfo2 = AccessToolsExtensions.DeclaredMethod(typeof(StringBuilder), "AppendLine", new Type[1] { typeof(string) }, (Type[])null);
		MethodInfo methodInfo3 = AccessToolsExtensions.DeclaredMethod(typeof(StatWorker), "GearAffectsStat", (Type[])null, (Type[])null);
		CodeMatcher val = new CodeMatcher(instructions, (ILGenerator)null);
		List<CodeMatch> list = new List<CodeMatch>
		{
			CodeMatch.LoadsArgument(false, (string)null),
			CodeMatch.LoadsArgument(false, (string)null),
			CodeMatch.LoadsLocal(false, (string)null),
			CodeMatch.LoadsArgument(false, (string)null),
			new CodeMatch((OpCode?)OpCodes.Ldfld, (object)null, (string)null),
			CodeMatch.Calls(methodInfo),
			CodeMatch.Calls((MethodInfo)null),
			CodeMatch.Calls(methodInfo2),
			new CodeMatch((OpCode?)OpCodes.Pop, (object)null, (string)null)
		};
		List<CodeMatch> list2 = new List<CodeMatch>
		{
			CodeMatch.LoadsLocal(false, (string)null),
			new CodeMatch((OpCode?)OpCodes.Ldfld, (object)null, (string)null),
			CodeMatch.LoadsArgument(false, (string)null),
			new CodeMatch((OpCode?)OpCodes.Ldfld, (object)null, (string)null),
			CodeMatch.Calls(methodInfo3),
			CodeMatch.Branches((string)null)
		};
		int num = -5;
		int num2 = 1;
		int num3 = -6;
		string[] array = new string[2] { "apparel", "gear" };
		foreach (string text in array)
		{
			val.Reset(true);
			if (text == "gear")
			{
				list.InsertRange(3, new _003C_003Ez__ReadOnlyArray<CodeMatch>((CodeMatch[])(object)new CodeMatch[2]
				{
					new CodeMatch((OpCode?)OpCodes.Ldfld, (object)null, (string)null),
					CodeMatch.Calls((MethodInfo)null)
				}));
				list2.InsertRange(2, new _003C_003Ez__ReadOnlyArray<CodeMatch>((CodeMatch[])(object)new CodeMatch[2]
				{
					CodeMatch.Calls((MethodInfo)null),
					new CodeMatch((OpCode?)OpCodes.Ldfld, (object)null, (string)null)
				}));
				num = -7;
				num3 = -8;
				num2 = 3;
			}
			val.MatchEndForward(list.ToArray());
			if (val.IsValid)
			{
				val.Advance(-1);
				val.Instruction.opcode = OpCodes.Call;
				val.Operand = SymbolExtensions.GetMethodInfo((LambdaExpression)(Expression<Func<Func<StringBuilder, string, string, Thing, StatDef, StringBuilder>>>)(() => AppendOffsetsAndFactors));
				val.Insert((IEnumerable<CodeInstruction>)val.InstructionsWithOffsets(num3, -3));
			}
			else
			{
				Log.Error("[VEF] Failed patching stat explanations for " + text + ". Equipped " + text + " stat factors won't be displayed for pawns.");
			}
			val.Reset(true);
			val.MatchEndForward(list2.ToArray());
			if (val.IsValid)
			{
				val.Insert(GenCollection.Concat<CodeInstruction>(from x in val.InstructionsWithOffsets(num, -2)
					select x.Clone(), CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<bool, Thing, StatDef, bool>>>)(() => ApparelExtensionUtilities.GearAffectsStatsWrapper))));
				val.Advance(num2);
				val.RemoveInstruction();
			}
			else
			{
				Log.Error("[VEF] Failed patching stat explanations for " + text + ". Equipped stat factors may not be displayed on pawns, and hyperlinks to relevant gear not included.");
			}
		}
		return val.Instructions();
	}

	public static StringBuilder AppendOffsetsAndFactors(StringBuilder sb, string baseText, string whitespace, Thing gear, StatDef stat)
	{
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		if (StatWorker.StatOffsetFromGear(gear, stat) != 0f)
		{
			sb.AppendLine(baseText);
		}
		ApparelExtension modExtension = ((Def)gear.def).GetModExtension<ApparelExtension>();
		if (modExtension == null)
		{
			return sb;
		}
		if (!GenList.NullOrEmpty<StatModifier>((IList<StatModifier>)modExtension.equippedStatFactors))
		{
			float statFactorFromList = StatUtility.GetStatFactorFromList(modExtension.equippedStatFactors, stat);
			if (statFactorFromList != 1f)
			{
				sb.AppendLine(whitespace + "    " + ((Entity)gear).LabelCap + ": " + GenText.ToStringByStyle(statFactorFromList, stat.finalizeEquippedStatOffset ? stat.toStringStyle : stat.ToStringStyleUnfinalized, (ToStringNumberSense)2));
			}
		}
		return sb;
	}
}
