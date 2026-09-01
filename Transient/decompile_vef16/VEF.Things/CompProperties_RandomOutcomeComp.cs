using System.Collections.Generic;
using Verse;

namespace VEF.Things;

public class CompProperties_RandomOutcomeComp : CompProperties
{
	public List<string> canProvideTags = new List<string>();

	public CompProperties_RandomOutcomeComp()
	{
		base.compClass = typeof(RandomOutcomeComp);
	}
}
