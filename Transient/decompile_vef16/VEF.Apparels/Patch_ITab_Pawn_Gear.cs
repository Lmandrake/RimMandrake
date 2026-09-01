using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Apparels;

public static class Patch_ITab_Pawn_Gear
{
	[HarmonyPatch(typeof(ITab_Pawn_Gear), "TryDrawOverallArmor")]
	public static class VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor
	{
		public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
		{
			//IL_011a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0126: Expected O, but got Unknown
			//IL_012f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0135: Expected O, but got Unknown
			//IL_013d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0143: Expected O, but got Unknown
			//IL_0150: Unknown result type (might be due to invalid IL or missing references)
			//IL_0156: Expected O, but got Unknown
			//IL_015e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0164: Expected O, but got Unknown
			//IL_016c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0172: Expected O, but got Unknown
			//IL_017f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0185: Expected O, but got Unknown
			//IL_018d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0193: Expected O, but got Unknown
			//IL_019b: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a1: Expected O, but got Unknown
			//IL_01f2: Unknown result type (might be due to invalid IL or missing references)
			//IL_01fe: Expected O, but got Unknown
			//IL_0207: Unknown result type (might be due to invalid IL or missing references)
			//IL_020d: Expected O, but got Unknown
			//IL_0215: Unknown result type (might be due to invalid IL or missing references)
			//IL_021b: Expected O, but got Unknown
			//IL_0228: Unknown result type (might be due to invalid IL or missing references)
			//IL_022e: Expected O, but got Unknown
			//IL_0236: Unknown result type (might be due to invalid IL or missing references)
			//IL_023c: Expected O, but got Unknown
			//IL_0244: Unknown result type (might be due to invalid IL or missing references)
			//IL_024a: Expected O, but got Unknown
			//IL_0253: Unknown result type (might be due to invalid IL or missing references)
			//IL_0259: Expected O, but got Unknown
			//IL_0262: Unknown result type (might be due to invalid IL or missing references)
			//IL_0268: Expected O, but got Unknown
			List<CodeInstruction> list = instructions.ToList();
			MethodInfo methodInfo = AccessTools.Method(typeof(List<Apparel>), "get_Item", new Type[1] { typeof(int) }, (Type[])null);
			MethodInfo methodInfo2 = AccessTools.Method(typeof(List<BodyPartRecord>), "get_Item", new Type[1] { typeof(int) }, (Type[])null);
			MethodInfo methodInfo3 = AccessTools.Method(typeof(VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor), "ShieldFromApparel", (Type[])null, (Type[])null);
			MethodInfo methodInfo4 = AccessTools.Method(typeof(VanillaExpandedFramework_ITab_Pawn_Gear_TryDrawOverallArmor), "ShieldFromEquipment", (Type[])null, (Type[])null);
			MethodInfo methodInfo5 = AccessTools.PropertyGetter(typeof(ITab_Pawn_Gear), "SelPawnForGear");
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

		public static void ShieldFromApparel(ref float armourImportance, StatDef stat, Apparel apparel, BodyPartRecord part)
		{
			if (((Thing)(object)apparel).IsShield(out var shieldComp) && shieldComp.UsableNow && shieldComp.CoversBodyPart(part))
			{
				float num = Mathf.Clamp01(StatExtension.GetStatValue((Thing)(object)apparel, stat, true, -1) / 2f);
				armourImportance *= 1f - num;
			}
		}

		public static void ShieldFromEquipment(ref float armourImportance, StatDef stat, BodyPartRecord part, Pawn pawn)
		{
			if (pawn.equipment == null)
			{
				return;
			}
			foreach (ThingWithComps item in pawn.equipment.AllEquipmentListForReading)
			{
				if (((Thing)(object)item).IsShield(out var shieldComp) && shieldComp.UsableNow && shieldComp.CoversBodyPart(part))
				{
					float num = Mathf.Clamp01(StatExtension.GetStatValue((Thing)(object)item, stat, true, -1) / 2f);
					armourImportance *= 1f - num;
				}
			}
		}
	}
}
