using Verse;

namespace VEF.Weapons;

internal class Projectile_VisualEffectCompProperties : CompProperties
{
	public bool gaussDistortion;

	public bool lightningGlow;

	public Projectile_VisualEffectCompProperties()
	{
		base.compClass = typeof(Projectile_VisualEffectComp);
	}
}
