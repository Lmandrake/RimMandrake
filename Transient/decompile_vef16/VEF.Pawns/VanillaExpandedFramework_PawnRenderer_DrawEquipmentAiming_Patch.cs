using HarmonyLib;
using UnityEngine;
using VEF.Things;
using VEF.Weapons;
using Verse;
using Verse.AI;

namespace VEF.Pawns;

[HotSwappable]
[HarmonyPatch(typeof(PawnRenderUtility), "DrawEquipmentAiming")]
public static class VanillaExpandedFramework_PawnRenderer_DrawEquipmentAiming_Patch
{
	[HarmonyPriority(800)]
	public static void Prefix(Thing eq, ref Vector3 drawLoc, ref float aimAngle)
	{
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawnAsHolder = eq.GetPawnAsHolder();
		if (pawnAsHolder == null)
		{
			return;
		}
		ThingDefExtension modExtension = ((Def)eq.def).GetModExtension<ThingDefExtension>();
		if (modExtension != null && PawnRenderUtility.CarryWeaponOpenly(pawnAsHolder))
		{
			Rot4 rotation = ((Thing)pawnAsHolder).Rotation;
			Pawn_PathFollower pather = pawnAsHolder.pather;
			bool pawnMoving = pather != null && pather.Moving;
			ApplyWeaponDrawOffset(modExtension.weaponCarryDrawOffsets, rotation, pawnMoving, ref drawLoc, ref aimAngle);
			if (modExtension.weaponDraftedDrawOffsets != null && !pawnAsHolder.stances.curStance.StanceBusy)
			{
				ApplyWeaponDrawOffset(modExtension.weaponDraftedDrawOffsets, rotation, pawnMoving, ref drawLoc, ref aimAngle);
			}
		}
	}

	private static void ApplyWeaponDrawOffset(WeaponDrawOffsets offsets, Rot4 pawnRot, bool pawnMoving, ref Vector3 drawLoc, ref float aimAngle)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		if (offsets != null)
		{
			Offset offset = null;
			if (pawnRot == Rot4.South)
			{
				offset = offsets.south;
			}
			else if (pawnRot == Rot4.North)
			{
				offset = offsets.north;
			}
			else if (pawnRot == Rot4.East)
			{
				offset = offsets.east;
			}
			else if (pawnRot == Rot4.West)
			{
				offset = offsets.west;
			}
			if (offset != null)
			{
				Vector3 val = ((pawnMoving && offset.drawOffsetWhileMoving.HasValue) ? offset.drawOffsetWhileMoving.Value : offset.drawOffset);
				drawLoc += val;
				float num = ((pawnMoving && offset.angleOffsetWhileMoving.HasValue) ? offset.angleOffsetWhileMoving.Value : offset.angleOffset);
				aimAngle += num;
			}
		}
	}
}
