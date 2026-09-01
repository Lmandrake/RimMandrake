using System.Collections.Generic;
using System.Text;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class GaussProjectileLinearDamageWorker : GaussProjectileDamageWorker
{
	public override int DamageAmount(GaussProjectile projectile, Thing equipment, List<Thing> hitThings)
	{
		if (projectile.damageFalloff == 0f)
		{
			return ((ThingDef)projectile.def).projectile.GetDamageAmount(equipment, (StringBuilder)null);
		}
		int num = 0;
		for (int i = 0; i < hitThings.Count; i++)
		{
			if (hitThings[i] is Pawn)
			{
				num++;
			}
		}
		float num2 = 1f + projectile.damageFalloff * (float)num;
		if (num2 <= 0f)
		{
			return 0;
		}
		return Mathf.Max(0, Mathf.RoundToInt((float)((ThingDef)projectile.def).projectile.GetDamageAmount(equipment, (StringBuilder)null) * num2));
	}
}
