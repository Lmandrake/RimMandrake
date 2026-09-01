using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class CompHomingProjectile : ThingComp
{
	public Vector3 originLaunchCell;

	public bool isOffset;

	public Projectile Projectile
	{
		get
		{
			ThingWithComps parent = base.parent;
			return (Projectile)(object)((parent is Projectile) ? parent : null);
		}
	}

	public CompProperties_HomingProjectile Props => base.props as CompProperties_HomingProjectile;

	public Vector3 DispersionOffset => new Vector3(Rand.Range(0f - Props.initialDispersionFromTarget, Props.initialDispersionFromTarget), 0f, Rand.Range(0f - Props.initialDispersionFromTarget, Props.initialDispersionFromTarget));

	public bool CanChangeTrajectory()
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		Projectile projectile = Projectile;
		Vector3 val = Vector3Utility.Yto0(originLaunchCell);
		Vector3 val2 = Vector3Utility.Yto0(((LocalTargetInfo)(ref projectile.intendedTarget)).CenterVector3);
		Vector3 val3 = Vector3Utility.Yto0(projectile.ExactPosition);
		Thing thing = ((LocalTargetInfo)(ref projectile.intendedTarget)).Thing;
		Pawn val4 = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val4 != null && val4.Dead)
		{
			return false;
		}
		float num = Vector3.Distance(val, val3);
		float num2 = Vector3.Distance(val, val2);
		if (num / num2 >= Props.homingDistanceFractionPassed)
		{
			return (float)Find.TickManager.TicksGame % Props.homingCorrectionTickRate == 0f;
		}
		return false;
	}

	public override void PostExposeData()
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<Vector3>(ref originLaunchCell, "originLaunchCell", default(Vector3), false);
	}
}
