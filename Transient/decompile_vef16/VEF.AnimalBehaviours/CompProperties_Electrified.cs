using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_Electrified : CompProperties
{
	public int electroRate;

	public int electroRadius;

	public int electroChargeAmount = 1;

	public List<string> batteriesToAffect;

	public CompProperties_Electrified()
	{
		base.compClass = typeof(CompElectrified);
	}
}
