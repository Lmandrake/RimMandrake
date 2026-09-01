using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_HighlyFlammable : HediffCompProperties
{
	public DamageDef damageToInflict;

	public float damageAmount = 15f;

	public int tickInterval = 50;

	public bool sunlightBurns;

	public HediffCompProperties_HighlyFlammable()
	{
		base.compClass = typeof(HediffComp_HighlyFlammable);
	}
}
