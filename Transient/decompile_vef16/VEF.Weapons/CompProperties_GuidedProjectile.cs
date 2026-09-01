using Verse;

namespace VEF.Weapons;

public class CompProperties_GuidedProjectile : CompProperties
{
	public float hitChance;

	public bool selectDifferentTargets;

	public CompProperties_GuidedProjectile()
	{
		base.compClass = typeof(CompGuidedProjectile);
	}
}
