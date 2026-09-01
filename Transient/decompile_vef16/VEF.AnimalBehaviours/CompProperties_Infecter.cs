using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_Infecter : CompProperties
{
	public int infectionChance = 10;

	public bool worsenExistingInfection;

	public float severityToAdd = 0.15f;

	public CompProperties_Infecter()
	{
		base.compClass = typeof(CompInfecter);
	}
}
