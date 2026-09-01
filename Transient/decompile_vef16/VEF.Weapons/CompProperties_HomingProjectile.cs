using Verse;

namespace VEF.Weapons;

public class CompProperties_HomingProjectile : CompProperties
{
	public float homingDistanceFractionPassed;

	public float homingCorrectionTickRate;

	public float initialDispersionFromTarget;

	public SoundDef hitSound;

	public CompProperties_HomingProjectile()
	{
		base.compClass = typeof(CompHomingProjectile);
	}
}
