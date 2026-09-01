using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_DiseasesAfterPeriod : CompProperties
{
	public int timeToApplyInTicks = 1000;

	public List<HediffDef> hediffsToApply;

	public float percentageOfMaxToReapply = 0.8f;

	public CompProperties_DiseasesAfterPeriod()
	{
		base.compClass = typeof(CompDiseasesAfterPeriod);
	}
}
