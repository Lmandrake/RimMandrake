using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Memes;

public static class VanillaExpandedFramework_IdeoUIUtility_AddPrecept_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator generator)
	{
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Expected O, but got Unknown
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Expected O, but got Unknown
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Expected O, but got Unknown
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Expected O, but got Unknown
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Expected O, but got Unknown
		//IL_011c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0122: Expected O, but got Unknown
		List<CodeInstruction> list = instructions.ToList();
		MethodInfo info1 = AccessTools.Method(typeof(WindowStack), "Add", (Type[])null, (Type[])null);
		int num = list.FindIndex((CodeInstruction ins) => CodeInstructionExtensions.Calls(ins, info1));
		Label label = generator.DefineLabel();
		Label label2 = generator.DefineLabel();
		list[num].labels.Add(label);
		list.InsertRange(num, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[2]
		{
			new CodeInstruction(OpCodes.Br, (object)label),
			CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Newobj, (object)AccessTools.Constructor(typeof(Dialog_FloatMenuOptions), new Type[1] { typeof(List<FloatMenuOption>) }, false)), new Label[1] { label2 })
		});
		list.InsertRange(num - 1, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[4]
		{
			new CodeInstruction(OpCodes.Dup, (object)null),
			new CodeInstruction(OpCodes.Callvirt, (object)AccessTools.PropertyGetter(typeof(List<FloatMenuOption>), "Count")),
			new CodeInstruction(OpCodes.Ldc_I4, (object)30),
			new CodeInstruction(OpCodes.Bge, (object)label2)
		});
		return list;
	}
}
