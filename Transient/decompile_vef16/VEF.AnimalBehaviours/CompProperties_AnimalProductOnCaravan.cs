using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_AnimalProductOnCaravan : CompProperties
{
	public int gatheringIntervalTicks = 30000;

	public int resourceAmount = 1;

	public ThingDef resourceDef;

	public bool femaleOnly;

	public CompProperties_AnimalProductOnCaravan()
	{
		base.compClass = typeof(CompAnimalProductOnCaravan);
	}
}
