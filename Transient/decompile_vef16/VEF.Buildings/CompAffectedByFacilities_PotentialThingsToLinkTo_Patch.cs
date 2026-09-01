using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class CompAffectedByFacilities_PotentialThingsToLinkTo_Patch
{
	private static bool Prepare()
	{
		return VanillaExpandedFramework_CompAffectedByFacilities_CanPotentiallyLinkTo_Patch.isActive;
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		int i;
		for (i = 0; i < 100; i++)
		{
			val.MatchEndForward((CodeMatch[])(object)new CodeMatch[2]
			{
				new CodeMatch((Func<CodeInstruction, bool>)((CodeInstruction op) => CodeInstructionExtensions.IsLdloc(op, (LocalBuilder)null) && CodeInstructionExtensions.LocalIndex(op) == 7), (string)null),
				CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(Thing), "def"), false)
			});
			if (val.IsInvalid)
			{
				break;
			}
			val.InsertAfter((CodeInstruction[])(object)new CodeInstruction[1] { CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<ThingDef, ThingDef>>>)(() => GetEquivalentFacility)) });
		}
		if (i != 3)
		{
			Log.Error(string.Format("Patched incorrect amount of instructions for {0}.{1}. Expected: {2}, patched: {3}.", "CompAffectedByFacilities", "PotentialThingsToLinkTo", 3, i));
		}
		return val.Instructions();
	}

	private static ThingDef GetEquivalentFacility(ThingDef def)
	{
		return ((Def)def).GetModExtension<FacilityExtension>()?.equivalentToFacility ?? def;
	}
}
