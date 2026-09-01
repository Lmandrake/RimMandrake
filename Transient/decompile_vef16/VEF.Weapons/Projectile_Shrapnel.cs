using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Weapons;

public class Projectile_Shrapnel : Projectile_Explosive
{
	public ProjectileProperties_Shrapnel Props => ((Thing)this).def.projectile as ProjectileProperties_Shrapnel;

	protected override void Tick()
	{
		((Projectile)this).Tick();
		if (Gen.IsHashIntervalTick((Thing)(object)this, 5) && ((Thing)this).def.projectile.SpeedTilesPerTick * (float)((Projectile)this).ticksToImpact <= Props.shrapnelRange)
		{
			((Projectile_Explosive)this).Explode();
		}
	}

	protected override void Explode()
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_0106: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		SoundStarter.PlayOneShot(((Thing)this).def.projectile.soundExplode, SoundInfo.op_Implicit((Thing)(object)this));
		for (int i = 0; i < Props.shrapnelCount; i++)
		{
			float num = Vector3Utility.AngleToFlat(((Projectile)this).origin, ((Projectile)this).destination) + Rand.Range(0f - Props.angleVariance, Props.angleVariance);
			float num2 = ((Thing)this).def.projectile.SpeedTilesPerTick * (float)((Projectile)this).ticksToImpact;
			Thing val = ThingMaker.MakeThing(Props.shrapnelProjectile, (ThingDef)null);
			Vector3 val2 = ((Projectile)this).ExactPosition + Vector3Utility.RotatedBy(Vector3.right * num2, num) - Gen.RandomHorizontalVector(0.15f);
			GenSpawn.Spawn(val, IntVec3Utility.ToIntVec3(((Projectile)this).ExactPosition), ((Thing)this).Map, (WipeMode)0);
			if (val is Projectile_ShrapnelPiece projectile_ShrapnelPiece)
			{
				projectile_ShrapnelPiece.Launch(((Projectile)this).launcher, ((Projectile)this).ExactPosition, val2, ((Projectile)this).equipmentDef, ((Projectile)this).equipment);
				continue;
			}
			Projectile val3 = (Projectile)(object)((val is Projectile) ? val : null);
			if (val3 != null)
			{
				val3.Launch(((Projectile)this).launcher, ((Projectile)this).ExactPosition, LocalTargetInfo.op_Implicit(IntVec3Utility.ToIntVec3(val2)), LocalTargetInfo.op_Implicit(IntVec3Utility.ToIntVec3(val2)), (ProjectileHitFlags)(-1), false, (Thing)null, (ThingDef)null);
			}
			else
			{
				val.Rotation = Rot4.FromAngleFlat(num);
			}
		}
		((Thing)this).Destroy((DestroyMode)0);
	}
}
