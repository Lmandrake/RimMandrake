using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_ExtremeXenophobia : CompProperties
{
	public int berserkRate = 10000;

	public List<string> AcceptedDefnames;

	public CompProperties_ExtremeXenophobia()
	{
		base.compClass = typeof(CompExtremeXenophobia);
	}
}
