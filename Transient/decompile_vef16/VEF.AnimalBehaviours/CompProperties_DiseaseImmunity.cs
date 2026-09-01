using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_DiseaseImmunity : CompProperties
{
	public List<string> hediffsToRemove;

	public int tickInterval = 250;

	public CompProperties_DiseaseImmunity()
	{
		base.compClass = typeof(CompDiseaseImmunity);
	}
}
