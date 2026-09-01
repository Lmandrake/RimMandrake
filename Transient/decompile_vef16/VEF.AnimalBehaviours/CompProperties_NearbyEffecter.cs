using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

internal class CompProperties_NearbyEffecter : CompProperties
{
	public List<string> thingsToAffect;

	public List<string> thingsToConvertTo;

	public int ticksConversionRate = 1000;

	public int radius = 2;

	public bool feedCauser;

	public float nutritionGained;

	public bool isForbidden;

	public CompProperties_NearbyEffecter()
	{
		base.compClass = typeof(CompNearbyEffecter);
	}
}
