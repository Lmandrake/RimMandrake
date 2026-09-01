using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(Projectile), "ImpactSomething")]
public static class VanillaExpandedFramework_Projectile_ImpactSomething_Patch
{
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions, ILGenerator ilg)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo addRangedDodge = AccessTools.Method(typeof(VanillaExpandedFramework_Projectile_ImpactSomething_Patch), "AddRangedDodge", (Type[])null, (Type[])null);
		MethodInfo impact = AccessTools.Method(typeof(Projectile), "Impact", (Type[])null, (Type[])null);
		Label label = ilg.DefineLabel();
		bool foundStloc = false;
		for (int i = 0; i < codes.Count; i++)
		{
			if (!foundStloc && codes[i].opcode == OpCodes.Stloc_S && codes[i].operand is LocalBuilder { LocalIndex: 5 })
			{
				foundStloc = true;
				yield return CodeInstruction.LoadLocal(6, false);
				yield return CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<Pawn, float>>>)(() => GetHitChanceFactor));
				yield return new CodeInstruction(OpCodes.Mul, (object)null);
				yield return codes[i];
			}
			else if (i > 1 && codes[i].opcode == OpCodes.Stloc_2 && codes[i - 1].opcode == OpCodes.Isinst && CodeInstructionExtensions.OperandIs(codes[i - 1], (MemberInfo)typeof(Pawn)))
			{
				codes[i + 1].labels.Add(label);
				yield return new CodeInstruction(OpCodes.Stloc_2, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloc_2, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)addRangedDodge);
				yield return new CodeInstruction(OpCodes.Brfalse_S, (object)label);
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldnull, (object)null);
				yield return new CodeInstruction(OpCodes.Ldc_I4_0, (object)null);
				yield return new CodeInstruction(OpCodes.Callvirt, (object)impact);
				yield return new CodeInstruction(OpCodes.Ret, (object)null);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static bool AddRangedDodge(Pawn pawn)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		if (pawn != null && Rand.Chance(StatExtension.GetStatValue((Thing)(object)pawn, InternalDefOf.VEF_RangedDodgeChance, true, -1)))
		{
			MoteMaker.ThrowText(((Thing)pawn).DrawPos, ((Thing)pawn).Map, TaggedString.op_Implicit(Translator.Translate("TextMote_Dodge")), 1.9f);
			return true;
		}
		return false;
	}

	public static float GetHitChanceFactor(Pawn pawn)
	{
		return 1f - StatExtension.GetStatValue((Thing)(object)pawn, InternalDefOf.VEF_RangedDodgeChance, true, -1);
	}
}
