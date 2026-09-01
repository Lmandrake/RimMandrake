using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_GasProducer : HediffCompProperties
{
	public int amount;

	public int timer;

	public GasType gasType;

	public HediffCompProperties_GasProducer()
	{
		base.compClass = typeof(HediffComp_GasProducer);
	}
}
