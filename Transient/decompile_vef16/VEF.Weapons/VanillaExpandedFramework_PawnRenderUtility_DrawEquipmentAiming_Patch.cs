using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_PawnRenderUtility_DrawEquipmentAiming_Patch
{
	private static bool recursionCheck;

	private static Pawn storedPawn;

	private static PawnRenderFlags storedFlags;

	private static Rot4 storedFacing;

	public static void GrabPawn(Pawn pawn, PawnRenderFlags flags, Rot4 facing)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		storedPawn = pawn;
		storedFlags = flags;
		storedFacing = facing;
	}

	public static void DrawDuplicate(Thing eq, ref Vector3 drawLoc, float aimAngle)
	{
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		if (recursionCheck || !StaticCollectionsClass.uniqueWeaponsInGame.Contains(eq.def))
		{
			return;
		}
		recursionCheck = true;
		CompUniqueWeapon val = ThingCompUtility.TryGetComp<CompUniqueWeapon>(eq);
		if (val == null)
		{
			return;
		}
		foreach (WeaponTraitDef item in val.TraitsListForReading)
		{
			WeaponTraitDefExtension modExtension = ((Def)item).GetModExtension<WeaponTraitDefExtension>();
			if (modExtension != null && modExtension.drawDuplicate)
			{
				PawnRenderUtility.DrawEquipmentAndApparelExtras(storedPawn, drawLoc + new Vector3(0f, 0f, 0.2f), storedFacing, storedFlags);
				drawLoc -= new Vector3(0f, 0f, -0.2f);
			}
		}
	}

	public static void DrawDuplicateCleanup()
	{
		recursionCheck = false;
		storedPawn = null;
	}
}
