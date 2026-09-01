using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class HediffToBodyparts
{
	public HediffDef hediff;

	public List<ConditionalStatAffecter> conditionals;

	public List<PrerequisiteSet> prerequisiteSets;

	public List<BodyPartDef> bodyparts = new List<BodyPartDef>();
}
