using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_FilthProducer : HediffCompProperties
{
	public string filthType = "";

	public float rate;

	public int radius;

	public int ticksToCreateFilth = 600;

	public HediffCompProperties_FilthProducer()
	{
		base.compClass = typeof(HediffComp_FilthProducer);
	}
}
