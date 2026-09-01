using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using VEF.Apparels;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(CompProjectileInterceptor), "PostDraw")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_CompProjectileInterceptor_PostDraw_Patch
{
	public static bool patchActive;

	private static bool Prepare(MethodBase baseMethod)
	{
		return patchActive;
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		int num = 0;
		for (int i = 0; i < 15; i++)
		{
			val.MatchEndForward((CodeMatch[])(object)new CodeMatch[3]
			{
				CodeMatch.IsLdarg((int?)0),
				CodeMatch.Calls(AccessToolsExtensions.DeclaredPropertyGetter(typeof(CompProjectileInterceptor), "Props")),
				CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(CompProperties_ProjectileInterceptor), "color"), false)
			});
			if (!val.IsValid)
			{
				break;
			}
			val.InsertAfter((CodeInstruction[])(object)new CodeInstruction[2]
			{
				CodeInstruction.LoadArgument(0, false),
				CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<Color, CompProjectileInterceptor, Color>>>)(() => ColorWrapper))
			});
			num++;
		}
		if (num != 2)
		{
			Log.Error(string.Format("[VEF] Patched incorrect amount of instructions for {0}.{1}. Expected: {2}, patched: {3}.", "CompProjectileInterceptor", "PostDraw", 2, num));
		}
		return val.Instructions();
	}

	private static Color ColorWrapper(Color color, CompProjectileInterceptor interceptor)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		ProjectileInterceptorExtension modExtension = ((Def)((Thing)((ThingComp)interceptor).parent).def).GetModExtension<ProjectileInterceptorExtension>();
		if (modExtension == null || GenList.NullOrEmpty<HealthColorPoint>((IList<HealthColorPoint>)modExtension.healthColorPoints))
		{
			return color;
		}
		float healthPercent = (float)interceptor.currentHitPoints / (float)interceptor.HitPointsMax;
		HealthColorPoint healthColorPoint = GenCollection.FirstOrDefault<HealthColorPoint>(modExtension.healthColorPoints, (Predicate<HealthColorPoint>)((HealthColorPoint p) => p.healthPercent >= healthPercent));
		HealthColorPoint healthColorPoint2 = modExtension.healthColorPoints.LastOrDefault((HealthColorPoint p) => p.healthPercent < healthPercent);
		if (healthColorPoint == null)
		{
			if (healthColorPoint2 == null)
			{
				return color;
			}
			return Color.Lerp(healthColorPoint2.color, color, Mathf.InverseLerp(healthColorPoint2.healthPercent, 1f, healthPercent));
		}
		if (healthColorPoint2 == null)
		{
			return healthColorPoint.color;
		}
		return Color.Lerp(healthColorPoint2.color, healthColorPoint.color, Mathf.InverseLerp(healthColorPoint2.healthPercent, healthColorPoint.healthPercent, healthPercent));
	}
}
