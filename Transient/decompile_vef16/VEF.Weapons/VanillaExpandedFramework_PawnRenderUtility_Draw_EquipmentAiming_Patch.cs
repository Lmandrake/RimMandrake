using System;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(PawnRenderUtility), "DrawEquipmentAiming", new Type[]
{
	typeof(Thing),
	typeof(Vector3),
	typeof(float)
})]
[StaticConstructorOnStartup]
public static class VanillaExpandedFramework_PawnRenderUtility_Draw_EquipmentAiming_Patch
{
	private static void Prefix(Thing eq, ref Vector3 drawLoc, ref float aimAngle)
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawnAsHolder = eq.GetPawnAsHolder();
		if (pawnAsHolder == null || !(eq is IDrawnWeaponWithRotation drawnWeaponWithRotation))
		{
			return;
		}
		Stance curStance = pawnAsHolder.stances.curStance;
		Stance_Busy val = (Stance_Busy)(object)((curStance is Stance_Busy) ? curStance : null);
		if (val != null && !val.neverAimWeapon)
		{
			LocalTargetInfo focusTarg = val.focusTarg;
			if (((LocalTargetInfo)(ref focusTarg)).IsValid)
			{
				drawLoc -= Vector3Utility.RotatedBy(new Vector3(0f, 0f, 0.4f), aimAngle);
				aimAngle = (aimAngle + drawnWeaponWithRotation.RotationOffset) % 360f;
				drawLoc += Vector3Utility.RotatedBy(new Vector3(0f, 0f, 0.4f), aimAngle);
			}
		}
	}
}
