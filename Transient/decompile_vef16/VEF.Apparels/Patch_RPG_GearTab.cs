using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

public static class Patch_RPG_GearTab
{
	public static Type DetailedRPGGearTab;

	public static Type DetailedRPGGearTabRevamped;

	public static IEnumerable<CodeInstruction> TryDrawOverallArmor_Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_0121: Expected O, but got Unknown
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Expected O, but got Unknown
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Expected O, but got Unknown
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0151: Expected O, but got Unknown
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Expected O, but got Unknown
		//IL_0167: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Expected O, but got Unknown
		//IL_017a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Expected O, but got Unknown
		//IL_0188: Unknown result type (might be due to invalid IL or missing references)
		//IL_018e: Expected O, but got Unknown
		//IL_0196: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Expected O, but got Unknown
		//IL_01ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f9: Expected O, but got Unknown
		//IL_0202: Unknown result type (might be due to invalid IL or missing references)
		//IL_0208: Expected O, but got Unknown
		//IL_0210: Unknown result type (might be due to invalid IL or missing references)
		//IL_0216: Expected O, but got Unknown
		//IL_0223: Unknown result type (might be due to invalid IL or missing references)
		//IL_0229: Expected O, but got Unknown
		//IL_0231: Unknown result type (might be due to invalid IL or missing references)
		//IL_0237: Expected O, but got Unknown
		//IL_023f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0245: Expected O, but got Unknown
		//IL_024e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0254: Expected O, but got Unknown
		//IL_025d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0263: Expected O, but got Unknown
		List<CodeInstruction> list = instructions.ToList();
		MethodInfo methodInfo = AccessTools.Method(typeof(List<Apparel>), "get_Item", new Type[1] { typeof(int) }, (Type[])null);
		MethodInfo methodInfo2 = AccessTools.Method(typeof(List<BodyPartRecord>), "get_Item", new Type[1] { typeof(int) }, (Type[])null);
		MethodInfo methodInfo3 = AccessTools.Method(typeof(Patch_ITab_Pawn_Gear.VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor), "ShieldFromApparel", (Type[])null, (Type[])null);
		MethodInfo methodInfo4 = AccessTools.Method(typeof(Patch_ITab_Pawn_Gear.VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor), "ShieldFromEquipment", (Type[])null, (Type[])null);
		MethodInfo methodInfo5 = AccessTools.PropertyGetter(DetailedRPGGearTab, "SelPawnForGear");
		int num = list.FindIndex((CodeInstruction ins) => ins.opcode == OpCodes.Stloc_S && ins.operand is LocalBuilder localBuilder && localBuilder.LocalIndex == 6);
		int num2 = list.FindIndex(num + 1, (CodeInstruction ins) => ins.opcode == OpCodes.Stloc_S && ins.operand is LocalBuilder localBuilder2 && localBuilder2.LocalIndex == 6);
		List<Label> list2 = CodeInstructionExtensions.ExtractLabels(list[num2 + 2]);
		list.InsertRange(num2 + 1, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[9]
		{
			CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Ldloca_S, (object)6), (IEnumerable<Label>)list2),
			new CodeInstruction(OpCodes.Ldarg_3, (object)null),
			new CodeInstruction(OpCodes.Ldloc_3, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)8),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo),
			new CodeInstruction(OpCodes.Ldloc_2, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)5),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo2),
			new CodeInstruction(OpCodes.Call, (object)methodInfo3)
		});
		int index = list.FindIndex((CodeInstruction ins) => ins.opcode == OpCodes.Ldloc_0);
		List<Label> list3 = CodeInstructionExtensions.ExtractLabels(list[index]);
		list.InsertRange(index, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[8]
		{
			CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Ldloca_S, (object)6), (IEnumerable<Label>)list3),
			new CodeInstruction(OpCodes.Ldarg_3, (object)null),
			new CodeInstruction(OpCodes.Ldloc_2, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)5),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo2),
			new CodeInstruction(OpCodes.Ldarg_0, (object)null),
			new CodeInstruction(OpCodes.Call, (object)methodInfo5),
			new CodeInstruction(OpCodes.Call, (object)methodInfo4)
		});
		return list;
	}

	public static IEnumerable<CodeInstruction> TryDrawOverallArmor1_Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_0121: Expected O, but got Unknown
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Expected O, but got Unknown
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Expected O, but got Unknown
		//IL_014c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Expected O, but got Unknown
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Expected O, but got Unknown
		//IL_0168: Unknown result type (might be due to invalid IL or missing references)
		//IL_016e: Expected O, but got Unknown
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0181: Expected O, but got Unknown
		//IL_0189: Unknown result type (might be due to invalid IL or missing references)
		//IL_018f: Expected O, but got Unknown
		//IL_0197: Unknown result type (might be due to invalid IL or missing references)
		//IL_019d: Expected O, but got Unknown
		//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fa: Expected O, but got Unknown
		//IL_0203: Unknown result type (might be due to invalid IL or missing references)
		//IL_0209: Expected O, but got Unknown
		//IL_0211: Unknown result type (might be due to invalid IL or missing references)
		//IL_0217: Expected O, but got Unknown
		//IL_0224: Unknown result type (might be due to invalid IL or missing references)
		//IL_022a: Expected O, but got Unknown
		//IL_0232: Unknown result type (might be due to invalid IL or missing references)
		//IL_0238: Expected O, but got Unknown
		//IL_0240: Unknown result type (might be due to invalid IL or missing references)
		//IL_0246: Expected O, but got Unknown
		//IL_024f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0255: Expected O, but got Unknown
		//IL_025e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0264: Expected O, but got Unknown
		List<CodeInstruction> list = instructions.ToList();
		MethodInfo methodInfo = AccessTools.Method(typeof(List<Apparel>), "get_Item", new Type[1] { typeof(int) }, (Type[])null);
		MethodInfo methodInfo2 = AccessTools.Method(typeof(List<BodyPartRecord>), "get_Item", new Type[1] { typeof(int) }, (Type[])null);
		MethodInfo methodInfo3 = AccessTools.Method(typeof(Patch_ITab_Pawn_Gear.VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor), "ShieldFromApparel", (Type[])null, (Type[])null);
		MethodInfo methodInfo4 = AccessTools.Method(typeof(Patch_ITab_Pawn_Gear.VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor), "ShieldFromEquipment", (Type[])null, (Type[])null);
		MethodInfo methodInfo5 = AccessTools.PropertyGetter(DetailedRPGGearTab, "SelPawnForGear");
		int num = list.FindIndex((CodeInstruction ins) => ins.opcode == OpCodes.Stloc_S && ins.operand is LocalBuilder localBuilder && localBuilder.LocalIndex == 7);
		int num2 = list.FindIndex(num + 1, (CodeInstruction ins) => ins.opcode == OpCodes.Stloc_S && ins.operand is LocalBuilder localBuilder2 && localBuilder2.LocalIndex == 7);
		List<Label> list2 = CodeInstructionExtensions.ExtractLabels(list[num2 + 1]);
		list.InsertRange(num2 + 1, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[9]
		{
			CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Ldloca_S, (object)6), (IEnumerable<Label>)list2),
			new CodeInstruction(OpCodes.Ldarg_2, (object)null),
			new CodeInstruction(OpCodes.Ldloc_3, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)9),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo),
			new CodeInstruction(OpCodes.Ldloc_2, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)6),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo2),
			new CodeInstruction(OpCodes.Call, (object)methodInfo3)
		});
		int index = list.FindIndex((CodeInstruction ins) => ins.opcode == OpCodes.Ldloc_0);
		List<Label> list3 = CodeInstructionExtensions.ExtractLabels(list[index]);
		list.InsertRange(index, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[8]
		{
			CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Ldloca_S, (object)6), (IEnumerable<Label>)list3),
			new CodeInstruction(OpCodes.Ldarg_2, (object)null),
			new CodeInstruction(OpCodes.Ldloc_2, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)6),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo2),
			new CodeInstruction(OpCodes.Ldarg_0, (object)null),
			new CodeInstruction(OpCodes.Call, (object)methodInfo5),
			new CodeInstruction(OpCodes.Call, (object)methodInfo4)
		});
		return list;
	}

	public static IEnumerable<CodeInstruction> TryDrawOverallArmor_Revamped_Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_0121: Expected O, but got Unknown
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Expected O, but got Unknown
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Expected O, but got Unknown
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0151: Expected O, but got Unknown
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Expected O, but got Unknown
		//IL_0167: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Expected O, but got Unknown
		//IL_017a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Expected O, but got Unknown
		//IL_0188: Unknown result type (might be due to invalid IL or missing references)
		//IL_018e: Expected O, but got Unknown
		//IL_0196: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Expected O, but got Unknown
		//IL_01ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f9: Expected O, but got Unknown
		//IL_0202: Unknown result type (might be due to invalid IL or missing references)
		//IL_0208: Expected O, but got Unknown
		//IL_0210: Unknown result type (might be due to invalid IL or missing references)
		//IL_0216: Expected O, but got Unknown
		//IL_0223: Unknown result type (might be due to invalid IL or missing references)
		//IL_0229: Expected O, but got Unknown
		//IL_0231: Unknown result type (might be due to invalid IL or missing references)
		//IL_0237: Expected O, but got Unknown
		//IL_023f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0245: Expected O, but got Unknown
		//IL_024e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0254: Expected O, but got Unknown
		//IL_025d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0263: Expected O, but got Unknown
		List<CodeInstruction> list = instructions.ToList();
		MethodInfo methodInfo = AccessTools.Method(typeof(List<Apparel>), "get_Item", new Type[1] { typeof(int) }, (Type[])null);
		MethodInfo methodInfo2 = AccessTools.Method(typeof(List<BodyPartRecord>), "get_Item", new Type[1] { typeof(int) }, (Type[])null);
		MethodInfo methodInfo3 = AccessTools.Method(typeof(Patch_ITab_Pawn_Gear.VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor), "ShieldFromApparel", (Type[])null, (Type[])null);
		MethodInfo methodInfo4 = AccessTools.Method(typeof(Patch_ITab_Pawn_Gear.VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor), "ShieldFromEquipment", (Type[])null, (Type[])null);
		MethodInfo methodInfo5 = AccessTools.PropertyGetter(DetailedRPGGearTabRevamped, "SelPawnForGear");
		int num = list.FindIndex((CodeInstruction ins) => ins.opcode == OpCodes.Stloc_S && ins.operand is LocalBuilder localBuilder && localBuilder.LocalIndex == 6);
		int num2 = list.FindIndex(num + 1, (CodeInstruction ins) => ins.opcode == OpCodes.Stloc_S && ins.operand is LocalBuilder localBuilder2 && localBuilder2.LocalIndex == 6);
		List<Label> list2 = CodeInstructionExtensions.ExtractLabels(list[num2 + 1]);
		list.InsertRange(num2 + 1, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[9]
		{
			CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Ldloca_S, (object)6), (IEnumerable<Label>)list2),
			new CodeInstruction(OpCodes.Ldarg_3, (object)null),
			new CodeInstruction(OpCodes.Ldloc_3, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)7),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo),
			new CodeInstruction(OpCodes.Ldloc_2, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)5),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo2),
			new CodeInstruction(OpCodes.Call, (object)methodInfo3)
		});
		int index = list.FindIndex((CodeInstruction ins) => ins.opcode == OpCodes.Ldloc_0);
		List<Label> list3 = CodeInstructionExtensions.ExtractLabels(list[index]);
		list.InsertRange(index, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[8]
		{
			CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Ldloca_S, (object)6), (IEnumerable<Label>)list3),
			new CodeInstruction(OpCodes.Ldarg_3, (object)null),
			new CodeInstruction(OpCodes.Ldloc_2, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)5),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo2),
			new CodeInstruction(OpCodes.Ldarg_0, (object)null),
			new CodeInstruction(OpCodes.Call, (object)methodInfo5),
			new CodeInstruction(OpCodes.Call, (object)methodInfo4)
		});
		return list;
	}

	public static IEnumerable<CodeInstruction> TryDrawOverallArmor1_Revamped_Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_0141: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Expected O, but got Unknown
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_015d: Expected O, but got Unknown
		//IL_0165: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Expected O, but got Unknown
		//IL_0178: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Expected O, but got Unknown
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Expected O, but got Unknown
		//IL_0194: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Expected O, but got Unknown
		//IL_01a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ad: Expected O, but got Unknown
		//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bb: Expected O, but got Unknown
		//IL_01c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c9: Expected O, but got Unknown
		//IL_021a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0226: Expected O, but got Unknown
		//IL_0230: Unknown result type (might be due to invalid IL or missing references)
		//IL_0236: Expected O, but got Unknown
		//IL_023e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0244: Expected O, but got Unknown
		//IL_0251: Unknown result type (might be due to invalid IL or missing references)
		//IL_0257: Expected O, but got Unknown
		//IL_025f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0265: Expected O, but got Unknown
		//IL_026d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0273: Expected O, but got Unknown
		//IL_027c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0282: Expected O, but got Unknown
		//IL_028b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0291: Expected O, but got Unknown
		List<CodeInstruction> list = instructions.ToList();
		MethodInfo methodInfo = AccessTools.Method(typeof(List<Apparel>), "get_Item", new Type[1] { typeof(int) }, (Type[])null);
		MethodInfo methodInfo2 = AccessTools.Method(typeof(List<BodyPartRecord>), "get_Item", new Type[1] { typeof(int) }, (Type[])null);
		MethodInfo methodInfo3 = AccessTools.Method(typeof(Patch_ITab_Pawn_Gear.VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor), "ShieldFromApparel", (Type[])null, (Type[])null);
		MethodInfo methodInfo4 = AccessTools.Method(typeof(Patch_ITab_Pawn_Gear.VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor), "ShieldFromEquipment", (Type[])null, (Type[])null);
		MethodInfo methodInfo5 = AccessTools.PropertyGetter(DetailedRPGGearTabRevamped, "SelPawnForGear");
		object operand = list.Find((CodeInstruction ins) => ins.opcode == OpCodes.Ldarg_S).operand;
		int num = list.FindIndex((CodeInstruction ins) => ins.opcode == OpCodes.Stloc_S && ins.operand is LocalBuilder localBuilder && localBuilder.LocalIndex == 6);
		int num2 = list.FindIndex(num + 1, (CodeInstruction ins) => ins.opcode == OpCodes.Stloc_S && ins.operand is LocalBuilder localBuilder2 && localBuilder2.LocalIndex == 6);
		List<Label> list2 = CodeInstructionExtensions.ExtractLabels(list[num2 + 1]);
		list.InsertRange(num2 + 1, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[9]
		{
			CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Ldloca_S, (object)6), (IEnumerable<Label>)list2),
			new CodeInstruction(OpCodes.Ldarg_S, operand),
			new CodeInstruction(OpCodes.Ldloc_3, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)8),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo),
			new CodeInstruction(OpCodes.Ldloc_2, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)5),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo2),
			new CodeInstruction(OpCodes.Call, (object)methodInfo3)
		});
		int index = list.FindIndex((CodeInstruction ins) => ins.opcode == OpCodes.Ldloc_0);
		List<Label> list3 = CodeInstructionExtensions.ExtractLabels(list[index]);
		list.InsertRange(index, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[8]
		{
			CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Ldloca_S, (object)6), (IEnumerable<Label>)list3),
			new CodeInstruction(OpCodes.Ldarg_S, operand),
			new CodeInstruction(OpCodes.Ldloc_2, (object)null),
			new CodeInstruction(OpCodes.Ldloc_S, (object)5),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo2),
			new CodeInstruction(OpCodes.Ldarg_0, (object)null),
			new CodeInstruction(OpCodes.Call, (object)methodInfo5),
			new CodeInstruction(OpCodes.Call, (object)methodInfo4)
		});
		return list;
	}
}
