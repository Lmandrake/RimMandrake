using Verse;

namespace BigAndSmall;

public class CompProperties_SlimeCost : CompProperties_PoolCost
{
	public CompProperties_SlimeCost()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_SlimeCost);
	}
}
