using UnityEngine;
using Verse;

namespace VEF.Weapons;

internal class Projectile_VisualEffectComp : ThingComp
{
	public Projectile_VisualEffectCompProperties Props => (Projectile_VisualEffectCompProperties)(object)base.props;

	public Projectile Projectile => (Projectile)base.parent;

	public override void CompTickInterval(int delta)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		Projectile projectile = Projectile;
		Vector3 val = projectile.ExactRotation * Vector3.forward;
		Vector3 val2 = projectile.ExactPosition + val;
		if (GenView.ShouldSpawnMotesAt(val2, ((Thing)base.parent).Map, true))
		{
			float angle = Vector3Utility.AngleToFlat(Projectile.ExactPosition, val2) - 90f;
			float num = 0.01f * ((Thing)Projectile).def.projectile.speed;
			if (Props.lightningGlow)
			{
				VefFleckMaker.MakeLightningGlow(((Thing)base.parent).Map, val2, angle, num, Rand.Range(0.3f, 0.6f));
			}
			if (Props.gaussDistortion)
			{
				VefFleckMaker.MakeGaussDistortion(((Thing)base.parent).Map, val2, angle, num + Rand.Range(-15f, 15f), Rand.Range(0.2f, 0.5f));
			}
		}
	}
}
