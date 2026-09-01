using Verse;

namespace BigAndSmall;

public class CompProperties_SoulEnergyCost : CompProperties_PoolCost
{
	public CompProperties_SoulEnergyCost()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_SoulEnergyCost);
	}
}
