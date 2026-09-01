using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_ResearchProjectDef_CanBeResearchedAt_Lambda_Patch
{
	private static bool Prepare(MethodBase baseMethod)
	{
		if (baseMethod != null)
		{
			return true;
		}
		foreach (ThingDef allDef in DefDatabase<ThingDef>.AllDefs)
		{
			ResearchBuildingExtension modExtension = ((Def)allDef).GetModExtension<ResearchBuildingExtension>();
			if (modExtension != null && !GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)modExtension.equivalentFacilities))
			{
				return true;
			}
		}
		return false;
	}

	private static MethodBase TargetMethod()
	{
		return AccessToolsExtensions.FirstMethod(AccessToolsExtensions.FirstInner(typeof(ResearchProjectDef), (Func<Type, bool>)((Type x) => AccessToolsExtensions.DeclaredField(x, "affectedByFacilities") != null)), (Func<MethodInfo, bool>)((MethodInfo x) => x.Name.Contains("<CanBeResearchedAt>") && x.ReturnType == typeof(bool) && x.GetParameters().Length == 1 && x.GetParameters()[0].ParameterType == typeof(Thing)));
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Expected O, but got Unknown
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[9]
		{
			CodeMatch.IsLdarg((int?)1),
			CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(Thing), "def"), false),
			CodeMatch.IsLdarg((int?)0),
			new CodeMatch((OpCode?)OpCodes.Ldfld, (object)null, (string)null),
			CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(ResearchProjectDef), "requiredResearchFacilities"), false),
			CodeMatch.IsLdarg((int?)0),
			new CodeMatch((OpCode?)OpCodes.Ldfld, (object)null, (string)null),
			CodeMatch.Calls((MethodInfo)null),
			CodeMatch.Branches((string)null)
		});
		val.Opcode = OpCodes.Brfalse_S;
		val.Insert((CodeInstruction[])(object)new CodeInstruction[1] { CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<ThingDef, ThingDef, bool>>>)(() => AreFacilitiesEquivalent)) });
		return val.Instructions();
	}

	private static bool AreFacilitiesEquivalent(ThingDef actualFacility, ThingDef requiredFacility)
	{
		if (actualFacility == requiredFacility)
		{
			return true;
		}
		ResearchBuildingExtension modExtension = ((Def)requiredFacility).GetModExtension<ResearchBuildingExtension>();
		if (modExtension != null && !GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)modExtension.equivalentFacilities))
		{
			return modExtension.equivalentFacilities.Contains(actualFacility);
		}
		return false;
	}
}
