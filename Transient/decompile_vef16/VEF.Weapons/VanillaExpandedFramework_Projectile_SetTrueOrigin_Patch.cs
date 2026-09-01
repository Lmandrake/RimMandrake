using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch]
public static class VanillaExpandedFramework_Projectile_SetTrueOrigin_Patch
{
	public static MethodInfo InterceptChanceFactorFromDistanceInfo = AccessToolsExtensions.Method(typeof(VerbUtility), "InterceptChanceFactorFromDistance", (Type[])null, (Type[])null);

	public static FieldInfo Projectile_origin = AccessToolsExtensions.Field(typeof(Projectile), "origin");

	public static IEnumerable<MethodBase> TargetMethods()
	{
		yield return AccessToolsExtensions.Method(typeof(Projectile), "CheckForFreeInterceptBetween", (Type[])null, (Type[])null);
		yield return AccessToolsExtensions.Method(typeof(Projectile), "CheckForFreeIntercept", (Type[])null, (Type[])null);
		yield return AccessToolsExtensions.Method(typeof(Projectile), "ImpactSomething", (Type[])null, (Type[])null);
	}

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions, MethodBase baseMethod)
	{
		bool patched = false;
		List<CodeInstruction> codes = codeInstructions.ToList();
		for (int i = 0; i < codes.Count; i++)
		{
			CodeInstruction val = codes[i];
			bool shouldPatch = CodeInstructionExtensions.LoadsField(val, Projectile_origin, false) && codes.Skip(i + 1).Any((CodeInstruction c) => CodeInstructionExtensions.Calls(c, InterceptChanceFactorFromDistanceInfo));
			yield return val;
			if (shouldPatch)
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_Projectile_SetTrueOrigin_Patch), "GetTrueOrigin", (Type[])null, (Type[])null));
				patched = true;
			}
		}
		if (!patched)
		{
			Log.Error("[VEF] Error patching homing projectiles - couldn't patch Projectile.origin in " + baseMethod.DeclaringType?.Namespace + "." + baseMethod.DeclaringType?.Name + ":" + baseMethod.Name);
		}
	}

	public static Vector3 GetTrueOrigin(Vector3 origin, Projectile projectile)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		if (projectile.IsHomingProjectile(out var comp))
		{
			return comp.originLaunchCell;
		}
		return origin;
	}
}
