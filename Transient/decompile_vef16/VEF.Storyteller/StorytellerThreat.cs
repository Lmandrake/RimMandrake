using System;
using System.Collections.Generic;
using Verse;

namespace VEF.Storyteller;

public class StorytellerThreat : IExposable
{
	public IntRange naturallGoodwillForAllFactions;

	public int disableThreatsAtPopulationCount;

	public float allDamagesMultiplier;

	public List<string> goodIncidents = new List<string>();

	public IntRange? raidWarningRange;

	public void ExposeData()
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		Scribe_Values.Look<IntRange>(ref naturallGoodwillForAllFactions, "naturallGoodwillForAllFactions", default(IntRange), false);
		Scribe_Values.Look<IntRange?>(ref raidWarningRange, "raidWarningRange", (IntRange?)null, false);
		Scribe_Values.Look<int>(ref disableThreatsAtPopulationCount, "disableThreatsAtPopulationCount", 0, false);
		Scribe_Values.Look<float>(ref allDamagesMultiplier, "allDamagesMultiplier", 0f, false);
		Scribe_Collections.Look<string>(ref goodIncidents, "goodIncidents", (LookMode)1, Array.Empty<object>());
	}
}
