using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_StatWorker_RelevantGear_Transpiler
{
	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Expected O, but got Unknown
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Expected O, but got Unknown
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Expected O, but got Unknown
		MethodInfo methodInfo = AccessToolsExtensions.DeclaredMethod(typeof(StatWorker), "GearAffectsStat", (Type[])null, (Type[])null);
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.Start();
		string[] array = new string[2] { "apparel", "gear" };
		foreach (string text in array)
		{
			val.MatchEndForward((CodeMatch[])(object)new CodeMatch[6]
			{
				CodeMatch.LoadsLocal(false, (string)null),
				new CodeMatch((OpCode?)OpCodes.Ldfld, (object)null, (string)null),
				CodeMatch.LoadsArgument(false, (string)null),
				new CodeMatch((OpCode?)OpCodes.Ldfld, (object)null, (string)null),
				CodeMatch.Calls(methodInfo),
				CodeMatch.Branches((string)null)
			});
			if (val.IsValid)
			{
				val.Insert(GenCollection.Concat<CodeInstruction>(from x in val.InstructionsWithOffsets(-5, -2)
					select x.Clone(), CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<bool, Thing, StatDef, bool>>>)(() => ApparelExtensionUtilities.GearAffectsStatsWrapper))));
				val.Advance(1);
				val.RemoveInstruction();
			}
			else
			{
				Log.Error("[VEF] Failed patching stat explanations for " + text + ". Equipped stat factors may not be displayed on pawns, and hyperlinks to relevant gear not included.");
			}
		}
		return val.Instructions();
	}
}
