using System.Collections.Generic;
using Verse;

namespace VEF.Apparels;

public class CompProperties_ApparelHediffs : CompProperties
{
	public List<string> hediffDefnames;

	public CompProperties_ApparelHediffs()
	{
		base.compClass = typeof(CompApparelHediffs);
	}
}
