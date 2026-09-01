using RimWorld;
using Verse;

namespace VEF.Hediffs;

public class HediffCompProperties_DamageAura : HediffCompProperties_Draw
{
	public DamageDef damageDef;

	public float damageAmount = -1f;

	public float armorPenetration = -1f;

	public int ticksBetween;

	public float radius;

	public SoundDef sustainer;

	public SoundDef soundEnded;

	public bool hostileOnly = true;

	public TargetingParameters targetingParameters = new TargetingParameters
	{
		canTargetPawns = true,
		canTargetBuildings = true
	};
}
