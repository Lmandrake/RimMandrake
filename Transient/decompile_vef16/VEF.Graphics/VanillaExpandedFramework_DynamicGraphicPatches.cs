using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

[HarmonyPatch]
public static class VanillaExpandedFramework_DynamicGraphicPatches
{
	[HarmonyPatch(typeof(PawnRenderUtility), "DrawEquipmentAiming")]
	[HarmonyPrefix]
	[HarmonyPriority(0)]
	public static bool DrawEquipmentAimingPrefix(Thing eq, Vector3 drawLoc, float aimAngle)
	{
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0114: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		if (eq is DynamicGraphicThing dynamicGraphicThing)
		{
			Vector3 val3 = default(Vector3);
			float num2 = default(float);
			foreach (Graphic dynamicGraphic in dynamicGraphicThing.GetDynamicGraphics())
			{
				float num = aimAngle - 90f;
				Mesh val;
				if (aimAngle > 20f && aimAngle < 160f)
				{
					val = MeshPool.plane10;
					num += eq.def.equippedAngleOffset;
				}
				else if (aimAngle > 200f && aimAngle < 340f)
				{
					val = MeshPool.plane10Flip;
					num -= 180f;
					num -= eq.def.equippedAngleOffset;
				}
				else
				{
					val = MeshPool.plane10;
					num += eq.def.equippedAngleOffset;
				}
				num %= 360f;
				CompEquippable val2 = ThingCompUtility.TryGetComp<CompEquippable>(eq);
				if (val2 != null)
				{
					EquipmentUtility.Recoil(eq.def, EquipmentUtility.GetRecoilVerb(val2.AllVerbs), ref val3, ref num2, aimAngle);
					drawLoc += val3;
					num += num2;
				}
				Vector3 val4 = Vector3Utility.RotatedBy(dynamicGraphic.DrawOffset(Rot4.South), num);
				Material val5 = dynamicGraphic.MatSingleFor(eq);
				Vector3 val6 = new Vector3(dynamicGraphic.drawSize.x, 0f, dynamicGraphic.drawSize.y);
				Matrix4x4 val7 = Matrix4x4.TRS(drawLoc + val4, Quaternion.AngleAxis(num, Vector3.up), val6);
				Graphics.DrawMesh(val, val7, val5, 0);
			}
			return false;
		}
		return true;
	}
}
