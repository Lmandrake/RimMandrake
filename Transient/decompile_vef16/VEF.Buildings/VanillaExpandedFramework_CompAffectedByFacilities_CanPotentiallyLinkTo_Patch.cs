using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(CompAffectedByFacilities), "CanPotentiallyLinkTo")]
[HarmonyPatch(new Type[]
{
	typeof(ThingDef),
	typeof(IntVec3),
	typeof(Rot4)
})]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_CompAffectedByFacilities_CanPotentiallyLinkTo_Patch
{
	public static bool isActive;

	private static bool Prepare()
	{
		return isActive;
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[7]
		{
			CodeMatch.IsLdarg((int?)0),
			CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(CompAffectedByFacilities), "linkedFacilities"), false),
			CodeMatch.IsLdloc((LocalBuilder)null),
			CodeMatch.Calls(AccessToolsExtensions.DeclaredIndexerGetter(typeof(List<Thing>), new Type[1] { typeof(int) })),
			CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(Thing), "def"), false),
			CodeMatch.IsLdarg((int?)1),
			CodeMatch.Branches((string)null)
		});
		val.Opcode = OpCodes.Brfalse_S;
		val.Insert((CodeInstruction[])(object)new CodeInstruction[1] { CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<ThingDef, ThingDef, bool>>>)(() => FacilityExtension.AreFacilitiesEquivalent)) });
		return val.Instructions();
	}
}
