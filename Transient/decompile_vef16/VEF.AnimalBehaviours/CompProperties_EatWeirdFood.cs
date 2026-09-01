using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_EatWeirdFood : CompProperties
{
	public List<string> customThingToEat;

	public int nutrition = 2;

	public bool fullyDestroyThing;

	public float percentageOfDestruction = 0.1f;

	public bool ignoreUseHitPoints;

	public bool digThingIfMapEmpty;

	public string thingToDigIfMapEmpty = "";

	public int customAmountToDig = 1;

	public string hediffWhenEaten = "";

	public bool advanceLifeStage;

	public int advanceAfterXFeedings = 1;

	public string defToAdvanceTo = "";

	public bool fissionAfterXFeedings;

	public string defToFissionTo = "";

	public int numberOfOffspring = 2;

	public bool fissionOnlyIfTamed = true;

	public bool drainBattery;

	public float percentageDrain = 0.1f;

	public bool areFoodSourcesPlants;

	public bool needsWater = true;

	public CompProperties_EatWeirdFood()
	{
		base.compClass = typeof(CompEatWeirdFood);
	}
}
