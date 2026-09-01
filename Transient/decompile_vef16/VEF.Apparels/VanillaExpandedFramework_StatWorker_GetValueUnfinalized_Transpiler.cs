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

[HarmonyPatch(typeof(StatWorker), "GetValueUnfinalized")]
public static class VanillaExpandedFramework_StatWorker_GetValueUnfinalized_Transpiler
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		List<CodeInstruction> codes = instructions.ToList();
		MethodInfo statOffsetFromGearMethod = AccessTools.Method(typeof(StatWorker), "StatOffsetFromGear", (Type[])null, (Type[])null);
		MethodInfo getItemMethod = AccessToolsExtensions.DeclaredIndexerGetter(typeof(List<Apparel>), new Type[1] { typeof(int) });
		MethodInfo getPrimaryMethod = AccessToolsExtensions.DeclaredPropertyGetter(typeof(Pawn_EquipmentTracker), "Primary");
		FieldInfo statField = AccessToolsExtensions.DeclaredField(typeof(StatWorker), "stat");
		bool foundApparel = false;
		bool foundGear = false;
		object apparelIdx = 20;
		for (int i = 0; i < codes.Count; i++)
		{
			yield return codes[i];
			if (!foundApparel && codes[i].opcode == OpCodes.Ldloc_S && CodeInstructionExtensions.Calls(codes[i + 1], getItemMethod))
			{
				apparelIdx = codes[i].operand;
			}
			else
			{
				if (!(codes[i].opcode == OpCodes.Stloc_0) || !(codes[i - 1].opcode == OpCodes.Add) || !CodeInstructionExtensions.Calls(codes[i - 2], statOffsetFromGearMethod))
				{
					continue;
				}
				if (!foundApparel && CodeInstructionExtensions.Calls(codes[i - 5], getItemMethod))
				{
					foundApparel = true;
					yield return CodeInstruction.LoadLocal(0, true);
					yield return CodeInstruction.LoadLocal(1, false);
					yield return CodeInstruction.LoadField(typeof(Pawn), "apparel", false);
					yield return new CodeInstruction(OpCodes.Callvirt, (object)AccessToolsExtensions.DeclaredPropertyGetter(typeof(Pawn_ApparelTracker), "WornApparel"));
					yield return new CodeInstruction(OpCodes.Ldloc_S, apparelIdx);
					yield return new CodeInstruction(OpCodes.Callvirt, (object)getItemMethod);
					yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
					yield return new CodeInstruction(OpCodes.Ldfld, (object)statField);
					yield return CodeInstruction.Call((LambdaExpression)(Expression<Func<_003C_003EA_007B00000001_007D<float, Thing, StatDef>>>)(() => ModifyStatsForGear));
				}
				else if (!foundGear && CodeInstructionExtensions.Calls(codes[i - 5], getPrimaryMethod))
				{
					foundGear = true;
					yield return CodeInstruction.LoadLocal(0, true);
					yield return CodeInstruction.LoadLocal(1, false);
					yield return CodeInstruction.LoadField(typeof(Pawn), "equipment", false);
					yield return CodeInstruction.LoadArgument(0, false);
					yield return new CodeInstruction(OpCodes.Ldfld, (object)statField);
					yield return CodeInstruction.Call((LambdaExpression)(Expression<Func<_003C_003EA_007B00000001_007D<float, Pawn_EquipmentTracker, StatDef>>>)(() => ModifyStatsForAllEquipment));
				}
			}
		}
		if (!foundApparel)
		{
			Log.Error("[VEF] Failed patching stat factors for apparel.");
		}
		if (!foundGear)
		{
			Log.Error("[VEF] Failed patching stat factors for gear.");
		}
	}

	private static void ModifyStatsForAllEquipment(ref float value, Pawn_EquipmentTracker equipment, StatDef stat)
	{
		foreach (ThingWithComps item in equipment.AllEquipmentListForReading)
		{
			ModifyStatsForGear(ref value, (Thing)(object)item, stat);
		}
	}

	public static void ModifyStatsForGear(ref float value, Thing gear, StatDef stat)
	{
		ApparelExtension apparelExtension = ((gear != null) ? ((Def)gear.def).GetModExtension<ApparelExtension>() : null);
		if (apparelExtension != null && !GenList.NullOrEmpty<StatModifier>((IList<StatModifier>)apparelExtension.equippedStatFactors))
		{
			value *= StatUtility.GetStatFactorFromList(apparelExtension.equippedStatFactors, stat);
		}
	}

	public static float StatFactorFromGear(Apparel gear, StatDef stat)
	{
		ApparelExtension apparelExtension = ((gear != null) ? ((Def)((Thing)gear).def).GetModExtension<ApparelExtension>() : null);
		if (apparelExtension != null && !GenList.NullOrEmpty<StatModifier>((IList<StatModifier>)apparelExtension.equippedStatFactors))
		{
			return StatUtility.GetStatFactorFromList(apparelExtension.equippedStatFactors, stat);
		}
		return 1f;
	}
}
