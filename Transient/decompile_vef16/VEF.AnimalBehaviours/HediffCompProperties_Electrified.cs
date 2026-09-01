using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_Electrified : HediffCompProperties
{
	public int electroRate;

	public int electroRadius;

	public int electroChargeAmount = 1;

	public List<string> batteriesToAffect;

	public HediffCompProperties_Electrified()
	{
		base.compClass = typeof(HediffComp_Electrified);
	}
}
