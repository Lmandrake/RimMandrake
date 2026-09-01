using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(typeof(SectionLayer_LightingOverlay), "GenerateLightingOverlay")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_SectionLayer_LightingOverlay_GenerateLightingOverlay_Patch
{
	private static bool Prepare(MethodBase method)
	{
		if (method != null)
		{
			return true;
		}
		foreach (RoofDef allDef in DefDatabase<RoofDef>.AllDefs)
		{
			RoofExtension modExtension = ((Def)allDef).GetModExtension<RoofExtension>();
			if (modExtension != null && !modExtension.AlwaysDrawsShadow)
			{
				return true;
			}
		}
		return false;
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[3]
		{
			CodeMatch.IsLdloc((LocalBuilder)null),
			CodeMatch.IsLdloc((LocalBuilder)null),
			CodeMatch.Calls(AccessToolsExtensions.DeclaredMethod(typeof(RoofGrid), "RoofAt", new Type[1] { typeof(int) }, (Type[])null))
		});
		if (val.IsValid)
		{
			val.InsertAfter((CodeInstruction[])(object)new CodeInstruction[3]
			{
				CodeInstruction.LoadArgument(0, false),
				val.InstructionAt(-1).Clone(),
				CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<RoofDef, Map, int, RoofDef>>>)(() => RoofAtWrapper))
			});
		}
		else
		{
			Log.Error("Failed patching SectionLayer_LightingOverlay:GenerateLightingOverlay - unable to find target instructions.");
		}
		return val.Instructions();
	}

	private static RoofDef RoofAtWrapper(RoofDef def, Map map, int cellIndex)
	{
		RoofExtension roofExtension = ((def != null) ? ((Def)def).GetModExtension<RoofExtension>() : null);
		if (roofExtension != null && !roofExtension.ShouldDrawShadow(map, cellIndex, def))
		{
			return null;
		}
		return def;
	}
}
