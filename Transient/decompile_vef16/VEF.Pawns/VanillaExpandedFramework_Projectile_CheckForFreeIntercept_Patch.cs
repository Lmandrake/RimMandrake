using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(Projectile), "CheckForFreeIntercept")]
public class VanillaExpandedFramework_Projectile_CheckForFreeIntercept_Patch
{
	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Expected O, but got Unknown
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Expected O, but got Unknown
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Expected O, but got Unknown
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[8]
		{
			CodeMatch.LoadsConstant(0.4000000059604645),
			CodeMatch.LoadsLocal(false, (string)null),
			new CodeMatch((OpCode?)OpCodes.Callvirt, (object)null, (string)null),
			CodeMatch.LoadsConstant(0.10000000149011612),
			CodeMatch.LoadsConstant(2.0),
			new CodeMatch((OpCode?)OpCodes.Call, (object)null, (string)null),
			new CodeMatch((OpCode?)OpCodes.Mul, (object)null, (string)null),
			CodeMatch.StoresLocal((string)null)
		});
		val.Advance(-1);
		val.Insert((CodeInstruction[])(object)new CodeInstruction[3]
		{
			CodeInstruction.LoadLocal(7, false),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<Pawn, float>>>)(() => VanillaExpandedFramework_Projectile_ImpactSomething_Patch.GetHitChanceFactor)),
			new CodeInstruction(OpCodes.Mul, (object)null)
		});
		return val.Instructions();
	}
}
