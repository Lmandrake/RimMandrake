using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_ExplodeOnDamage : HediffCompProperties
{
	public int minDamageToExplode;

	public DamageDef damageType;

	public int damageAmount = -1;

	public float radius;

	public SoundDef sound;

	public ThingDef spawnThingDef;

	public float spawnThingChance;

	public HediffCompProperties_ExplodeOnDamage()
	{
		base.compClass = typeof(HediffComp_ExplodeOnDamage);
	}
}
