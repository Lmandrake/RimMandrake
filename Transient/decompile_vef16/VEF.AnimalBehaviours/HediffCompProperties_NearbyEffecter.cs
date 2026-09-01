using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_NearbyEffecter : HediffCompProperties
{
	public List<string> thingsToAffect;

	public List<string> thingsToConvertTo;

	public int ticksConversionRate = 1000;

	public int radius = 2;

	public bool feedCauser;

	public float nutritionGained;

	public bool isForbidden;

	public HediffCompProperties_NearbyEffecter()
	{
		base.compClass = typeof(HediffComp_NearbyEffecter);
	}
}
