using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class GravshipUtility_PreLaunchConfirmation_Patch
{
	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr, ILGenerator ilGenerator)
	{
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Expected O, but got Unknown
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Expected O, but got Unknown
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Expected O, but got Unknown
		//IL_0111: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Expected O, but got Unknown
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0144: Expected O, but got Unknown
		//IL_014c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Expected O, but got Unknown
		MethodInfo methodInfo = AccessToolsExtensions.DeclaredMethod(typeof(ThingCompUtility), "HasComp", (Type[])null, (Type[])null).MakeGenericMethod(typeof(CompOxygenPusher));
		MethodInfo methodInfo2 = AccessToolsExtensions.DeclaredMethod(typeof(GravshipUtility_PreLaunchConfirmation_Patch), "IsOxygenPusher", (Type[])null, (Type[])null);
		MethodInfo methodInfo3 = AccessToolsExtensions.DeclaredMethod(typeof(GravshipUtility_PreLaunchConfirmation_Patch), "IsHeater", (Type[])null, (Type[])null);
		CodeMatcher val = new CodeMatcher(instr, ilGenerator);
		val.MatchStartForward((CodeMatch[])(object)new CodeMatch[3]
		{
			CodeMatch.IsLdloc((LocalBuilder)null),
			CodeMatch.Calls(methodInfo),
			CodeMatch.Branches((string)null)
		});
		int num = CodeInstructionExtensions.LocalIndex(val.Instruction);
		Label label = default(Label);
		val.Advance(3).CreateLabel(ref label).Advance(-1)
			.Insert((CodeInstruction[])(object)new CodeInstruction[3]
			{
				new CodeInstruction(OpCodes.Brtrue, (object)label),
				CodeInstruction.LoadLocal(num, false),
				new CodeInstruction(OpCodes.Call, (object)methodInfo2)
			})
			.Start()
			.MatchEndForward((CodeMatch[])(object)new CodeMatch[3]
			{
				CodeMatch.IsLdloc((LocalBuilder)null),
				new CodeMatch((OpCode?)OpCodes.Isinst, (object)typeof(Building_Heater), (string)null),
				CodeMatch.Branches((string)null)
			})
			.Insert((CodeInstruction[])(object)new CodeInstruction[3]
			{
				CodeInstruction.LoadLocal(num, false),
				new CodeInstruction(OpCodes.Call, (object)methodInfo3),
				new CodeInstruction(val.Instruction)
			});
		return val.Instructions();
	}

	private static bool IsOxygenPusher(Thing thing)
	{
		return ((Def)thing.def).GetModExtension<GravshipLaunchExtension>()?.isOxygenPusher ?? false;
	}

	private static bool IsHeater(Thing thing)
	{
		return ((Def)thing.def).GetModExtension<GravshipLaunchExtension>()?.isHeater ?? false;
	}
}
