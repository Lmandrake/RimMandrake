using System.Collections.Generic;
using Verse;

namespace VEF.Weapons;

public abstract class GaussProjectileDamageWorker
{
	public ExpandableProjectileDef def;

	public abstract int DamageAmount(GaussProjectile projectile, Thing equipment, List<Thing> hitThings);
}
