using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_CompRefuelable_EjectFuelPatches
{
	public static bool patchActive;

	private static bool Prepare()
	{
		return patchActive;
	}

	private static IEnumerable<MethodBase> TargetMethods()
	{
		yield return AccessToolsExtensions.DeclaredMethod(typeof(CompRefuelable), "EjectFuel", (Type[])null, (Type[])null);
		yield return AccessToolsExtensions.DeclaredMethod(typeof(CompRefuelable), "PostDestroy", (Type[])null, (Type[])null);
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr, MethodBase baseMethod)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[1] { CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(CompRefuelable), "fuel"), false) });
		val.InsertAfter((CodeInstruction[])(object)new CodeInstruction[2]
		{
			CodeInstruction.LoadArgument(0, false),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<float, CompRefuelable, float>>>)(() => ApplyFuelMultiplier))
		});
		return val.Instructions();
	}

	private static float ApplyFuelMultiplier(float fuel, CompRefuelable __instance)
	{
		RefuelableExtension modExtension = ((Def)((Thing)((ThingComp)__instance).parent).def).GetModExtension<RefuelableExtension>();
		if (modExtension != null && modExtension.ejectingFuelRespectsFuelMultiplier)
		{
			return fuel / __instance.Props.FuelMultiplierCurrentDifficulty;
		}
		return fuel;
	}
}
