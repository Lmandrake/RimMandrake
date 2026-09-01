using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_Exploder : HediffCompProperties
{
	public float explosionForce = 5.9f;

	public DamageDef damageDef;

	public HediffCompProperties_Exploder()
	{
		base.compClass = typeof(HediffComp_Exploder);
	}
}
