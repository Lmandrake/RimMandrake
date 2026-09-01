using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Building_TurretGun), "DrawExtraSelectionOverlays")]
public static class VanillaExpandedFramework_Building_TurretGun_DrawExtraSelectionOverlays_Transpiler
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		List<CodeInstruction> codes = instructions.ToList();
		bool flag = false;
		for (int i = 0; i < codes.Count; i++)
		{
			if (codes[i].operand as MethodInfo == typeof(GenDraw).GetMethod("DrawRadiusRing", new Type[2]
			{
				typeof(IntVec3),
				typeof(float)
			}) && !flag)
			{
				flag = true;
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_Building_TurretGun_DrawExtraSelectionOverlays_Transpiler), "DrawConeForDirectionalTurret", (Type[])null, (Type[])null));
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static void DrawConeForDirectionalTurret(IntVec3 center, float radius, Building_TurretGun instance)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		if (!(((Building_Turret)instance).AttackVerb is Verb_ShootCone))
		{
			GenDraw.DrawRadiusRing(((Thing)instance).Position, radius);
		}
	}
}
