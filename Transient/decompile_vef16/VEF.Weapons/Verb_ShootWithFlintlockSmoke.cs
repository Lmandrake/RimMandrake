using System.Text;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class Verb_ShootWithFlintlockSmoke : Verb_Shoot
{
	protected override bool TryCastShot()
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		if (base.TryCastShot())
		{
			IntVec3 positionHeld = ((Verb)this).caster.PositionHeld;
			Vector3 loc = ((IntVec3)(ref positionHeld)).ToVector3();
			Map mapHeld = ((Verb)this).caster.MapHeld;
			ThingDef projectile = VerbUtility.GetProjectile((Verb)(object)this);
			int? num;
			if (projectile == null)
			{
				num = null;
			}
			else
			{
				ProjectileProperties projectile2 = projectile.projectile;
				num = ((projectile2 != null) ? new int?(projectile2.GetDamageAmount(((Verb)this).caster, (StringBuilder)null)) : ((int?)null));
			}
			float size = Mathf.Clamp01(((float?)num / 32f) ?? 1f);
			SmokeMaker.ThrowFlintLockSmoke(loc, mapHeld, size);
			SmokeMaker.ThrowFlintLockSmoke(loc, mapHeld, size);
			return true;
		}
		return false;
	}
}
