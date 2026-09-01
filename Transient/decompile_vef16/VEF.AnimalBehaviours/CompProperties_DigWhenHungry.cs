using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_DigWhenHungry : CompProperties
{
	public string customThingToDig = "";

	public int customAmountToDig = 1;

	public List<string> customThingsToDig;

	public List<int> customAmountsToDig;

	public int timeToDig = 40000;

	public List<string> acceptedTerrains;

	public bool spawnForbidden;

	public bool digAnywayEveryXTicks = true;

	public int timeToDigForced = 120000;

	public bool isFrostmite;

	public bool digOnlyOnGrowingSeason;

	public int minTemperature;

	public int maxTemperature = 58;

	public CompProperties_DigWhenHungry()
	{
		base.compClass = typeof(CompDigWhenHungry);
	}
}
