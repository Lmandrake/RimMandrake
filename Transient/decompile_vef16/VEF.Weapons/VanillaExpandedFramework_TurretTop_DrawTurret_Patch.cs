using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(TurretTop), "DrawTurret")]
[StaticConstructorOnStartup]
internal class VanillaExpandedFramework_TurretTop_DrawTurret_Patch
{
	private static bool Prefix(TurretTop __instance, Building_Turret ___parentTurret)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		if (!(___parentTurret is Building_LaserGun building_LaserGun))
		{
			return true;
		}
		float num = __instance.CurRotation;
		LocalTargetInfo targetCurrentlyAimingAt = ((Building_Turret)building_LaserGun).TargetCurrentlyAimingAt;
		if (((LocalTargetInfo)(ref targetCurrentlyAimingAt)).HasThing)
		{
			targetCurrentlyAimingAt = ((Building_Turret)building_LaserGun).TargetCurrentlyAimingAt;
			num = Vector3Utility.AngleFlat(((LocalTargetInfo)(ref targetCurrentlyAimingAt)).CenterVector3 - GenThing.TrueCenter((Thing)(object)building_LaserGun));
		}
		if (((Building_TurretGun)building_LaserGun).gun is IDrawnWeaponWithRotation drawnWeaponWithRotation)
		{
			num += drawnWeaponWithRotation.RotationOffset;
		}
		Material val = ((ThingDef)building_LaserGun.def).building.turretTopMat;
		if (((Building_TurretGun)building_LaserGun).gun is SpinningLaserGunTurret spinningLaserGunTurret)
		{
			spinningLaserGunTurret.turret = building_LaserGun;
			val = ((Thing)spinningLaserGunTurret).Graphic.MatSingle;
		}
		Vector3 val2 = default(Vector3);
		((Vector3)(ref val2))._002Ector(((ThingDef)building_LaserGun.def).building.turretTopOffset.x, 0f, ((ThingDef)building_LaserGun.def).building.turretTopOffset.y);
		float turretTopDrawSize = ((ThingDef)building_LaserGun.def).building.turretTopDrawSize;
		Matrix4x4 val3 = default(Matrix4x4);
		((Matrix4x4)(ref val3)).SetTRS(((Thing)building_LaserGun).DrawPos + Altitudes.AltIncVect + val2, GenMath.ToQuat(num), new Vector3(turretTopDrawSize, 1f, turretTopDrawSize));
		Graphics.DrawMesh(MeshPool.plane10, val3, val, 0);
		return false;
	}
}
