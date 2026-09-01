using Verse;

namespace VEF.Weapons;

public class TeslaChainingProps : DefModExtension
{
	public bool addFire;

	public float bounceRange;

	public int maxBounceCount;

	public DamageDef damageDef;

	public DamageDef explosionDamageDef;

	public float impactRadius;

	public bool targetFriendly;

	public int maxLifetime;

	public SoundDef impactSound;
}
