using UnityEngine;
using Verse;

namespace VEF.Cooking;

public class CompProperties_MaturingAlcohol : CompProperties
{
	public float daysToRotStart = 2f;

	public bool rotDestroys;

	public float rotDamagePerDay = 40f;

	public float daysToDessicated = 999f;

	public float dessicatedDamagePerDay;

	public bool disableIfHatcher;

	public string maturingString;

	public string maturingProperly;

	public string maturingSlowly;

	public string maturingStopped;

	public string thingToTransformTo;

	public int TicksToRotStart => Mathf.RoundToInt(daysToRotStart * 60000f);

	public int TicksToDessicated => Mathf.RoundToInt(daysToDessicated * 60000f);

	public CompProperties_MaturingAlcohol()
	{
		base.compClass = typeof(CompMaturingAlcohol);
	}

	public CompProperties_MaturingAlcohol(float daysToRotStart)
	{
		this.daysToRotStart = daysToRotStart;
	}
}
