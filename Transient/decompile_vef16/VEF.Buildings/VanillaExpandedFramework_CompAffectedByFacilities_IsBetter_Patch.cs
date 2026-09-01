using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(CompAffectedByFacilities), "IsBetter")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_CompAffectedByFacilities_IsBetter_Patch
{
	private static bool Prepare()
	{
		return VanillaExpandedFramework_CompAffectedByFacilities_CanPotentiallyLinkTo_Patch.isActive;
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[4]
		{
			CodeMatch.IsLdarg((int?)1),
			CodeMatch.IsLdarg((int?)4),
			CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(Thing), "def"), false),
			CodeMatch.Branches((string)null)
		});
		val.Opcode = OpCodes.Brtrue_S;
		val.Insert((CodeInstruction[])(object)new CodeInstruction[1] { CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<ThingDef, ThingDef, bool>>>)(() => FacilityExtension.AreFacilitiesEquivalent)) });
		return val.Instructions();
	}
}
