using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompPropertiesIntegrateGenes : CompProperties_AbilityEffect
{
	public CompPropertiesIntegrateGenes()
	{
		((AbilityCompProperties)this).compClass = typeof(CompProperticesIntegrateGenesEffect);
	}
}
