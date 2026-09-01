using System.Collections.Generic;
using System.Text;
using Verse;

namespace VEF.Weapons;

public class GaussProjectileDefaultDamageWorker : GaussProjectileDamageWorker
{
	public override int DamageAmount(GaussProjectile projectile, Thing equipment, List<Thing> hitThings)
	{
		int damageAmount = ((ThingDef)projectile.def).projectile.GetDamageAmount(equipment, (StringBuilder)null);
		float num = 1f;
		num += (float)projectile.hitThings.Count / 10f;
		return (int)((float)damageAmount / num);
	}
}
