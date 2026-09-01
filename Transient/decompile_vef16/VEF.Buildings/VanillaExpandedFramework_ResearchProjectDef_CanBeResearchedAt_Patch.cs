using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(ResearchProjectDef), "CanBeResearchedAt")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_ResearchProjectDef_CanBeResearchedAt_Patch
{
	private static bool? isPatchActive;

	public static bool IsPatchActive
	{
		get
		{
			bool valueOrDefault = isPatchActive == true;
			if (!isPatchActive.HasValue)
			{
				valueOrDefault = DefDatabase<ThingDef>.AllDefs.Any(delegate(ThingDef def)
				{
					ResearchBuildingExtension modExtension = ((Def)def).GetModExtension<ResearchBuildingExtension>();
					return modExtension != null && !GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)modExtension.equivalentBenches);
				});
				isPatchActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	private static bool Prepare()
	{
		return IsPatchActive;
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[5]
		{
			CodeMatch.IsLdarg((int?)1),
			CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(Thing), "def"), false),
			CodeMatch.IsLdarg((int?)0),
			CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(ResearchProjectDef), "requiredResearchBuilding"), false),
			CodeMatch.Branches((string)null)
		});
		val.Opcode = OpCodes.Brtrue_S;
		val.Insert((CodeInstruction[])(object)new CodeInstruction[1] { CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<ThingDef, ThingDef, bool>>>)(() => AreBenchesEquivalent)) });
		return val.Instructions();
	}

	private static bool AreBenchesEquivalent(ThingDef actualBench, ThingDef requiredBench)
	{
		if (actualBench == requiredBench)
		{
			return true;
		}
		ResearchBuildingExtension modExtension = ((Def)requiredBench).GetModExtension<ResearchBuildingExtension>();
		if (modExtension != null && !GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)modExtension.equivalentBenches))
		{
			return modExtension.equivalentBenches.Contains(actualBench);
		}
		return false;
	}
}
