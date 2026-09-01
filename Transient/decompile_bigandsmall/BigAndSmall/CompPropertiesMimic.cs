using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompPropertiesMimic : CompProperties_AbilityEffect
{
	public List<GeneDef> genesToRetain = new List<GeneDef>();

	public CompPropertiesMimic()
	{
		((AbilityCompProperties)this).compClass = typeof(CompPropertiesMimicffect);
	}
}
