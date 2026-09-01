using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_DigPeriodically : CompProperties
{
	public List<string> customThingToDig;

	public List<int> customAmountToDig;

	public int ticksToDig = 60000;

	public bool onlyWhenTamed;

	public bool spawnForbidden;

	public bool digBiomeRocks;

	public bool digBiomeBricks;

	public int customAmountToDigIfRocksOrBricks = 1;

	public bool resultIsCorpse;

	public bool onlyDigIfPolluted;

	public CompProperties_DigPeriodically()
	{
		base.compClass = typeof(CompDigPeriodically);
	}
}
