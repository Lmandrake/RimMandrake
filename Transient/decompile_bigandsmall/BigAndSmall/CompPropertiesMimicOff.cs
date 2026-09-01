using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompPropertiesMimicOff : CompProperties_AbilityEffect
{
	public List<GeneDef> genesToRetain = new List<GeneDef>();

	public bool spawnFilth = true;

	public CompPropertiesMimicOff()
	{
		((AbilityCompProperties)this).compClass = typeof(CompProperticesMimicOffEffect);
	}
}
