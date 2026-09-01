using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_Refueling : CompProperties
{
	public int fuelingRate;

	public int fuelingRadius;

	public List<string> buildingsToAffect;

	public bool mustBeTamed;

	public CompProperties_Refueling()
	{
		base.compClass = typeof(CompRefueling);
	}
}
