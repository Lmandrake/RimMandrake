using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_FilthProducer : CompProperties
{
	public string filthType = "";

	public float rate;

	public int radius;

	public int ticksToCreateFilth = 600;

	public CompProperties_FilthProducer()
	{
		base.compClass = typeof(CompFilthProducer);
	}
}
